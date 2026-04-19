from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ContentChunk(Base):
    __tablename__ = "content_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    module_id: Mapped[str] = mapped_column(ForeignKey("modules.id"), nullable=False)
    source_file: Mapped[str] = mapped_column(String, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    module: Mapped["Module"] = relationship(back_populates="content_chunks")  # noqa: F821
