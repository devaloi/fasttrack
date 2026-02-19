import enum
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class UserRole(enum.StrEnum):
    ADMIN = "admin"
    USER = "user"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    display_name: str = Field(max_length=100, default="")
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    projects: list["Project"] = Relationship(back_populates="owner")  # type: ignore[name-defined]  # noqa: F821
    assigned_tasks: list["Task"] = Relationship(back_populates="assignee")  # type: ignore[name-defined]  # noqa: F821
    comments: list["Comment"] = Relationship(back_populates="author")  # type: ignore[name-defined]  # noqa: F821
