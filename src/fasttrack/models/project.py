import enum
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class ProjectStatus(enum.StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: str = Field(default="")
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)
    owner_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    owner: "User" = Relationship(back_populates="projects")  # type: ignore[name-defined]  # noqa: F821
    tasks: list["Task"] = Relationship(back_populates="project")  # type: ignore[name-defined]  # noqa: F821
