from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from fasttrack.auth.dependencies import CurrentUser
from fasttrack.database import get_session
from fasttrack.models.project import Project
from fasttrack.models.task import Task, TaskPriority, TaskStatus
from fasttrack.models.user import UserRole
from fasttrack.schemas.pagination import PaginatedResponse
from fasttrack.schemas.task import TaskCreate, TaskRead, TaskUpdate
from fasttrack.utils.pagination import paginate

router = APIRouter(tags=["tasks"])


async def _get_project_for_owner(
    project_id: int, user_id: int, user_role: str, session: AsyncSession
) -> Project:
    result = await session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != user_id and user_role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not project owner")
    return project


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    project_id: int,
    data: TaskCreate,
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Task:
    await _get_project_for_owner(project_id, user.id, user.role, session)  # type: ignore[arg-type]
    task = Task(**data.model_dump(), project_id=project_id)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.get("/projects/{project_id}/tasks", response_model=PaginatedResponse[TaskRead])
async def list_tasks(
    project_id: int,
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    cursor: str | None = None,
    limit: int = 20,
    task_status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assignee_id: int | None = None,
) -> PaginatedResponse:
    await _get_project_for_owner(project_id, user.id, user.role, session)  # type: ignore[arg-type]
    query = select(Task).where(Task.project_id == project_id)
    if task_status:
        query = query.where(Task.status == task_status)
    if priority:
        query = query.where(Task.priority == priority)
    if assignee_id is not None:
        query = query.where(Task.assignee_id == assignee_id)
    return await paginate(session, query, Task, cursor=cursor, limit=limit)


@router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Task:
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    project_result = await session.execute(
        select(Project).where(Project.id == task.project_id)
    )
    project = project_result.scalar_one_or_none()
    if (
        project
        and project.owner_id != user.id
        and task.assignee_id != user.id
        and user.role != UserRole.ADMIN
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return task


@router.patch("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Task:
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    project_result = await session.execute(
        select(Project).where(Project.id == task.project_id)
    )
    project = project_result.scalar_one_or_none()
    if (
        project
        and project.owner_id != user.id
        and task.assignee_id != user.id
        and user.role != UserRole.ADMIN
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    task.updated_at = datetime.utcnow()
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    project_result = await session.execute(
        select(Project).where(Project.id == task.project_id)
    )
    project = project_result.scalar_one_or_none()
    if project and project.owner_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not project owner")
    await session.delete(task)
    await session.commit()
