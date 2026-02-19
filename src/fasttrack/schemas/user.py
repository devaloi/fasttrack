from datetime import datetime

from pydantic import BaseModel, EmailStr

from fasttrack.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: str = ""


class UserRead(BaseModel):
    id: int
    email: str
    display_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    display_name: str | None = None
    email: EmailStr | None = None


class UserAdminUpdate(BaseModel):
    role: UserRole | None = None
    is_active: bool | None = None
    display_name: str | None = None
