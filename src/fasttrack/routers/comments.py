from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from fasttrack.auth.dependencies import CurrentUser
from fasttrack.database import get_session
from fasttrack.models.comment import Comment
from fasttrack.models.project import Project
from fasttrack.models.task import Task
from fasttrack.models.user import UserRole
from fasttrack.schemas.comment import CommentCreate, CommentRead
from fasttrack.schemas.pagination import PaginatedResponse
from fasttrack.utils.pagination import paginate

router = APIRouter(tags=["comments"])


async def _check_task_access(
    task_id: int, user_id: int, user_role: str, session: AsyncSession
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
        and project.owner_id != user_id
        and task.assignee_id != user_id
        and user_role != UserRole.ADMIN
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return task


@router.post(
    "/tasks/{task_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    task_id: int,
    data: CommentCreate,
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Comment:
    await _check_task_access(task_id, user.id, user.role, session)  # type: ignore[arg-type]
    comment = Comment(body=data.body, task_id=task_id, author_id=user.id)  # type: ignore[arg-type]
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return comment


@router.get("/tasks/{task_id}/comments", response_model=PaginatedResponse[CommentRead])
async def list_comments(
    task_id: int,
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    cursor: str | None = None,
    limit: int = 20,
) -> PaginatedResponse:
    await _check_task_access(task_id, user.id, user.role, session)  # type: ignore[arg-type]
    query = select(Comment).where(Comment.task_id == task_id)
    return await paginate(session, query, Comment, cursor=cursor, limit=limit)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    result = await session.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.author_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not comment author"
        )
    await session.delete(comment)
    await session.commit()
