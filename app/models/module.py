from sqlalchemy import ARRAY, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    domain_id: Mapped[str] = mapped_column(ForeignKey("domains.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    difficulty: Mapped[str | None] = mapped_column(String)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    estimated_hours: Mapped[int | None] = mapped_column(Integer)
    git_path: Mapped[str | None] = mapped_column(String)
    last_reviewed: Mapped[Date | None] = mapped_column(Date)
    sota_topics: Mapped[list[str] | None] = mapped_column(ARRAY(Text))

    domain: Mapped["Domain"] = relationship(back_populates="modules")  # noqa: F821
    prerequisites: Mapped[list["ModulePrerequisite"]] = relationship(
        foreign_keys="ModulePrerequisite.module_id", back_populates="module"
    )
    required_by: Mapped[list["ModulePrerequisite"]] = relationship(
        foreign_keys="ModulePrerequisite.prereq_id", back_populates="prereq"
    )
    content_chunks: Mapped[list["ContentChunk"]] = relationship(back_populates="module")  # noqa: F821


class ModulePrerequisite(Base):
    __tablename__ = "module_prerequisites"

    module_id: Mapped[str] = mapped_column(ForeignKey("modules.id"), primary_key=True)
    prereq_id: Mapped[str] = mapped_column(ForeignKey("modules.id"), primary_key=True)

    module: Mapped["Module"] = relationship(foreign_keys=[module_id], back_populates="prerequisites")
    prereq: Mapped["Module"] = relationship(foreign_keys=[prereq_id], back_populates="required_by")
