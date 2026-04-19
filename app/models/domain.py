from sqlalchemy import ARRAY, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Domain(Base):
    __tablename__ = "domains"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str | None] = mapped_column(String)
    icon: Mapped[str | None] = mapped_column(String)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(Text))

    modules: Mapped[list["Module"]] = relationship(back_populates="domain")  # noqa: F821
