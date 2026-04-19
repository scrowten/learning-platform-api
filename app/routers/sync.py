from pathlib import Path

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import SyncLog
from scripts.sync import run_sync

router = APIRouter(prefix="/sync", tags=["sync"])


def _verify_secret(x_sync_secret: str = Header(default="")) -> None:
    if x_sync_secret != settings.sync_secret:
        raise HTTPException(status_code=401, detail="Invalid sync secret")


@router.post("/trigger")
async def trigger_sync(_: None = Depends(_verify_secret)):
    try:
        result = await run_sync(Path(settings.content_repo_path))
        return {"success": True, "data": result, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


@router.get("/status")
async def sync_status(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SyncLog).order_by(desc(SyncLog.synced_at)).limit(1)
    )
    log = result.scalar_one_or_none()
    if not log:
        return {"success": True, "data": {"status": "never_synced"}, "error": None}
    return {
        "success": True,
        "data": {
            "status": log.status,
            "domains_synced": log.domains_synced,
            "modules_synced": log.modules_synced,
            "error_message": log.error_message,
            "synced_at": log.synced_at.isoformat(),
        },
        "error": None,
    }
