from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from fasttrack.auth.dependencies import CurrentUser
from fasttrack.database import get_session
from fasttrack.models.project import Project
from fasttrack.models.user import UserRole
from fasttrack.schemas.pagination import PaginatedResponse
from fasttrack.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from fasttrack.utils.pagination import paginate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Project:
    project = Project(**data.model_dump(), owner_id=user.id)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


@router.get("", response_model=PaginatedResponse[ProjectRead])
async def list_projects(
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    cursor: str | None = None,
    limit: int = 20,
) -> PaginatedResponse:
    query = select(Project)
    if user.role != UserRole.ADMIN:
        query = query.where(Project.owner_id == user.id)
    return await paginate(session, query, Project, cursor=cursor, limit=limit)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int,
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Project:
    result = await session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not project owner")
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Project:
    result = await session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not project owner")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    project.updated_at = datetime.utcnow()
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    result = await session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not project owner")
    await session.delete(project)
    await session.commit()
