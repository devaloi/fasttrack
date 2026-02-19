from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Field, SQLModel, select


class BlockedToken(SQLModel, table=True):
    __tablename__ = "blocked_tokens"

    id: int | None = Field(default=None, primary_key=True)
    jti: str = Field(unique=True, index=True)
    blocked_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime


async def block_token(session: AsyncSession, jti: str, expires_at: datetime) -> None:
    token = BlockedToken(jti=jti, expires_at=expires_at)
    session.add(token)
    await session.commit()


async def is_blocked(session: AsyncSession, jti: str) -> bool:
    result = await session.execute(select(BlockedToken).where(BlockedToken.jti == jti))
    return result.scalar_one_or_none() is not None


async def cleanup_expired_tokens(session: AsyncSession) -> int:
    result = await session.execute(
        select(BlockedToken).where(BlockedToken.expires_at < datetime.utcnow())
    )
    expired = result.scalars().all()
    count = len(expired)
    for token in expired:
        await session.delete(token)
    await session.commit()
    return count
