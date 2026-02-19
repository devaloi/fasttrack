import base64
import json

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from fasttrack.schemas.pagination import PaginatedResponse

DEFAULT_PAGE_SIZE = 20


def encode_cursor(record_id: int) -> str:
    return base64.urlsafe_b64encode(json.dumps({"id": record_id}).encode()).decode()


def decode_cursor(cursor: str) -> int:
    try:
        data = json.loads(base64.urlsafe_b64decode(cursor))
        return int(data["id"])
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise ValueError("Invalid cursor") from e


async def paginate(
    session: AsyncSession,
    query: Select,
    model_class,  # noqa: ANN001
    cursor: str | None = None,
    limit: int = DEFAULT_PAGE_SIZE,
) -> PaginatedResponse:
    if cursor:
        last_id = decode_cursor(cursor)
        query = query.where(model_class.id > last_id)

    query = query.order_by(model_class.id).limit(limit + 1)
    result = await session.execute(query)
    rows = list(result.scalars().all())

    has_more = len(rows) > limit
    items = rows[:limit]

    next_cursor = None
    if has_more and items:
        next_cursor = encode_cursor(items[-1].id)

    return PaginatedResponse(items=items, next_cursor=next_cursor, has_more=has_more)
