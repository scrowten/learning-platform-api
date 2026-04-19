#!/usr/bin/env python3
"""
Sync worker: reads domain-registry.yaml + module frontmatter from the content
repo and upserts domains, modules, and prerequisites into PostgreSQL.

Idempotent — safe to run on every git push.

Usage:
    python scripts/sync.py [--repo-path /path/to/learning-platform]
"""
import asyncio
import re
import sys
from pathlib import Path

import yaml
from sqlalchemy import delete, text
from sqlalchemy.dialects.postgresql import insert

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.database import AsyncSessionLocal
from app.models import Domain, Module, ModulePrerequisite, SyncLog


def _extract_frontmatter(path: Path) -> dict | None:
    text_content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text_content, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def _load_registry(repo_path: Path) -> list[dict]:
    registry_path = repo_path / "domain-registry.yaml"
    if not registry_path.exists():
        raise FileNotFoundError(f"domain-registry.yaml not found at {registry_path}")
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    return data.get("domains", [])


def _load_modules(repo_path: Path, valid_domain_ids: set[str]) -> tuple[list[dict], list[dict]]:
    domains_dir = repo_path / "domains"
    modules = []
    prerequisites = []

    for readme in sorted(domains_dir.rglob("README.md")):
        if readme.parent.parent == domains_dir:
            continue

        fm = _extract_frontmatter(readme)
        if not fm or "id" not in fm or "domain" not in fm:
            continue
        if fm["domain"] not in valid_domain_ids:
            continue

        git_path = str(readme.parent.relative_to(repo_path))
        last_reviewed = fm.get("last_reviewed")
        if hasattr(last_reviewed, "isoformat"):
            last_reviewed = last_reviewed.isoformat()

        modules.append({
            "id": fm["id"],
            "domain_id": fm["domain"],
            "title": fm.get("title", fm["id"]),
            "difficulty": fm.get("difficulty"),
            "tags": fm.get("tags") or [],
            "estimated_hours": fm.get("estimated_hours"),
            "git_path": git_path,
            "last_reviewed": last_reviewed,
            "sota_topics": fm.get("sota_topics") or [],
        })

        for prereq_id in fm.get("prerequisites") or []:
            prerequisites.append({"module_id": fm["id"], "prereq_id": prereq_id})

    return modules, prerequisites


async def run_sync(repo_path: Path) -> dict:
    registry = _load_registry(repo_path)
    valid_domain_ids = {d["id"] for d in registry}
    modules, prerequisites = _load_modules(repo_path, valid_domain_ids)

    async with AsyncSessionLocal() as session:
        # Upsert domains
        for domain in registry:
            stmt = insert(Domain).values(
                id=domain["id"],
                name=domain["name"],
                path=domain["path"],
                color=domain.get("color"),
                icon=domain.get("icon"),
                tags=domain.get("tags") or [],
            ).on_conflict_do_update(
                index_elements=["id"],
                set_={"name": domain["name"], "path": domain["path"],
                      "color": domain.get("color"), "icon": domain.get("icon"),
                      "tags": domain.get("tags") or []},
            )
            await session.execute(stmt)

        # Upsert modules
        for module in modules:
            stmt = insert(Module).values(**module).on_conflict_do_update(
                index_elements=["id"],
                set_={k: v for k, v in module.items() if k != "id"},
            )
            await session.execute(stmt)

        # Replace prerequisites (delete + insert)
        module_ids = [m["id"] for m in modules]
        if module_ids:
            await session.execute(
                delete(ModulePrerequisite).where(
                    ModulePrerequisite.module_id.in_(module_ids)
                )
            )
        for prereq in prerequisites:
            await session.execute(insert(ModulePrerequisite).values(**prereq).on_conflict_do_nothing())

        # Write sync log
        log = SyncLog(
            status="success",
            domains_synced=len(registry),
            modules_synced=len(modules),
        )
        session.add(log)
        await session.commit()

    return {"domains_synced": len(registry), "modules_synced": len(modules)}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-path", default=settings.content_repo_path)
    args = parser.parse_args()

    result = asyncio.run(run_sync(Path(args.repo_path)))
    print(f"Sync complete: {result}")
