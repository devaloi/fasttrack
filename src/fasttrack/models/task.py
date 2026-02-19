import enum
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class TaskStatus(enum.StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(enum.StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=300)
    description: str = Field(default="")
    status: TaskStatus = Field(default=TaskStatus.TODO)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    project_id: int = Field(foreign_key="projects.id")
    assignee_id: int | None = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    project: "Project" = Relationship(back_populates="tasks")  # type: ignore[name-defined]  # noqa: F821
    assignee: "User" = Relationship(back_populates="assigned_tasks")  # type: ignore[name-defined]  # noqa: F821
    comments: list["Comment"] = Relationship(back_populates="task")  # type: ignore[name-defined]  # noqa: F821
