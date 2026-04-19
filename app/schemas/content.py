from datetime import date

from pydantic import BaseModel


class DomainOut(BaseModel):
    id: str
    name: str
    path: str
    color: str | None
    icon: str | None
    tags: list[str]

    model_config = {"from_attributes": True}


class ModuleOut(BaseModel):
    id: str
    domain_id: str
    title: str
    difficulty: str | None
    tags: list[str]
    estimated_hours: int | None
    git_path: str | None
    last_reviewed: date | None
    sota_topics: list[str]

    model_config = {"from_attributes": True}


class ModuleDetail(ModuleOut):
    prerequisites: list[str]


class ApiResponse(BaseModel):
    success: bool
    data: object
    error: str | None
    meta: dict | None = None
