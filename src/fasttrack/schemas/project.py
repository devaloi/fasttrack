from datetime import datetime

from pydantic import BaseModel

from fasttrack.models.project import ProjectStatus


class ProjectCreate(BaseModel):
    name: str
    description: str = ""


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str
    status: ProjectStatus
    owner_id: int
    created_at: datetime
    updated_at: datetime


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None
