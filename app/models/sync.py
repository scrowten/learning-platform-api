from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SyncLog(Base):
    __tablename__ = "sync_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String, nullable=False)  # success | error
    domains_synced: Mapped[int] = mapped_column(default=0)
    modules_synced: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
