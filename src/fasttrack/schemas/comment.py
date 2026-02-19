from datetime import datetime

from pydantic import BaseModel


class CommentCreate(BaseModel):
    body: str


class CommentRead(BaseModel):
    id: int
    body: str
    task_id: int
    author_id: int
    created_at: datetime
