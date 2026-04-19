from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Domain, Module, ModulePrerequisite

router = APIRouter(tags=["content"])


def _ok(data, meta=None):
    return {"success": True, "data": data, "error": None, "meta": meta}


def _module_to_dict(module: Module, include_prereqs: bool = False) -> dict:
    d = {
        "id": module.id,
        "domain_id": module.domain_id,
        "title": module.title,
        "difficulty": module.difficulty,
        "tags": module.tags or [],
        "estimated_hours": module.estimated_hours,
        "git_path": module.git_path,
        "last_reviewed": module.last_reviewed.isoformat() if module.last_reviewed else None,
        "sota_topics": module.sota_topics or [],
    }
    if include_prereqs:
        d["prerequisites"] = [p.prereq_id for p in module.prerequisites]
    return d


@router.get("/domains")
async def list_domains(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Domain).order_by(Domain.id))
    domains = result.scalars().all()
    return _ok([{"id": d.id, "name": d.name, "path": d.path,
                 "color": d.color, "icon": d.icon, "tags": d.tags or []}
                for d in domains])


@router.get("/domains/{domain_id}/modules")
async def list_domain_modules(
    domain_id: str,
    difficulty: str | None = Query(None),
    tags: list[str] = Query(default=[]),
    db: AsyncSession = Depends(get_db),
):
    domain = await db.get(Domain, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    stmt = (
        select(Module)
        .where(Module.domain_id == domain_id)
        .options(selectinload(Module.prerequisites))
    )
    if difficulty:
        stmt = stmt.where(Module.difficulty == difficulty)
    if tags:
        stmt = stmt.where(Module.tags.overlap(tags))

    result = await db.execute(stmt.order_by(Module.id))
    modules = result.scalars().all()
    total = len(modules)
    return _ok([_module_to_dict(m) for m in modules], meta={"total": total})


@router.get("/modules/{module_id}")
async def get_module(module_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Module)
        .where(Module.id == module_id)
        .options(selectinload(Module.prerequisites))
    )
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return _ok(_module_to_dict(module, include_prereqs=True))


@router.get("/modules/{module_id}/prerequisites")
async def get_prerequisites(module_id: str, db: AsyncSession = Depends(get_db)):
    module = await db.get(Module, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    result = await db.execute(
        select(Module)
        .join(ModulePrerequisite, Module.id == ModulePrerequisite.prereq_id)
        .where(ModulePrerequisite.module_id == module_id)
        .options(selectinload(Module.prerequisites))
    )
    prereqs = result.scalars().all()
    return _ok([_module_to_dict(p) for p in prereqs])


@router.get("/search")
async def search(
    q: str = Query(default=""),
    domain: str | None = Query(None),
    difficulty: str | None = Query(None),
    tags: list[str] = Query(default=[]),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Module).options(selectinload(Module.prerequisites))

    if q:
        stmt = stmt.where(
            or_(
                func.lower(Module.title).contains(q.lower()),
                Module.tags.any(func.lower(q)),
            )
        )
    if domain:
        stmt = stmt.where(Module.domain_id == domain)
    if difficulty:
        stmt = stmt.where(Module.difficulty == difficulty)
    if tags:
        stmt = stmt.where(Module.tags.overlap(tags))

    count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = count_result.scalar()

    stmt = stmt.offset((page - 1) * limit).limit(limit).order_by(Module.id)
    result = await db.execute(stmt)
    modules = result.scalars().all()

    return _ok(
        [_module_to_dict(m) for m in modules],
        meta={"total": total, "page": page, "limit": limit},
    )
