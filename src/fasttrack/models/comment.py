from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: int | None = Field(default=None, primary_key=True)
    body: str
    task_id: int = Field(foreign_key="tasks.id")
    author_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    task: "Task" = Relationship(back_populates="comments")  # type: ignore[name-defined]  # noqa: F821
    author: "User" = Relationship(back_populates="comments")  # type: ignore[name-defined]  # noqa: F821
