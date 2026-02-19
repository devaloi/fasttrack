from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

from fasttrack.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL, echo=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SQLModelAsyncSession(engine) as session:
        yield session


async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
