import logging
from datetime import UTC, datetime

from fasttrack.websocket.manager import manager

logger = logging.getLogger(__name__)


async def notify_task_assigned(task_id: int, project_name: str, assignee_id: int) -> None:
    await manager.send_to_user(assignee_id, {
        "type": "task_assigned",
        "data": {"task_id": task_id, "project": project_name},
        "timestamp": datetime.now(UTC).isoformat(),
    })


async def notify_comment_added(
    task_id: int, author_name: str, owner_id: int
) -> None:
    await manager.send_to_user(owner_id, {
        "type": "comment_added",
        "data": {"task_id": task_id, "author": author_name},
        "timestamp": datetime.now(UTC).isoformat(),
    })


async def notify_status_changed(
    task_id: int, old_status: str, new_status: str, owner_id: int
) -> None:
    await manager.send_to_user(owner_id, {
        "type": "status_changed",
        "data": {"task_id": task_id, "old": old_status, "new": new_status},
        "timestamp": datetime.now(UTC).isoformat(),
    })
