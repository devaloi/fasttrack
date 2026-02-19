from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from fasttrack.auth.dependencies import AdminUser, CurrentUser
from fasttrack.database import get_session
from fasttrack.models.user import User
from fasttrack.schemas.pagination import PaginatedResponse
from fasttrack.schemas.user import UserAdminUpdate, UserRead, UserUpdate
from fasttrack.utils.pagination import paginate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def get_me(user: CurrentUser) -> User:
    return user


@router.patch("/me", response_model=UserRead)
async def update_me(
    data: UserUpdate,
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    user.updated_at = datetime.utcnow()
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.get("", response_model=PaginatedResponse[UserRead])
async def list_users(
    admin: AdminUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    cursor: str | None = None,
    limit: int = 20,
) -> PaginatedResponse:
    query = select(User)
    return await paginate(session, query, User, cursor=cursor, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    admin: AdminUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def admin_update_user(
    user_id: int,
    data: UserAdminUpdate,
    admin: AdminUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    user.updated_at = datetime.utcnow()
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
