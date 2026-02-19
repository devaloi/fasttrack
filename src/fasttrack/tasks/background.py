import logging

logger = logging.getLogger(__name__)


async def send_assignment_email(task_title: str, assignee_email: str) -> None:
    logger.info("Email notification: Task '%s' assigned to %s", task_title, assignee_email)


async def update_project_stats(project_id: int) -> None:
    logger.info("Updating statistics for project %d", project_id)
