import asyncio
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

from fasttrack.auth.blocklist import BlockedToken  # noqa: F401
from fasttrack.auth.jwt import create_access_token
from fasttrack.auth.password import hash_password
from fasttrack.database import get_session
from fasttrack.main import create_app
from fasttrack.models import Comment, Project, Task, User  # noqa: F401
from fasttrack.models.user import UserRole

TEST_DB_URL = "sqlite+aiosqlite:///./test_fasttrack.db"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_engine():
    return create_async_engine(TEST_DB_URL, echo=False)


@pytest.fixture(autouse=True)
async def setup_db(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async with SQLModelAsyncSession(test_engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture
async def client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    async def override_session() -> AsyncGenerator[AsyncSession, None]:
        async with SQLModelAsyncSession(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(session: AsyncSession) -> User:
    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpass123"),
        display_name="Test User",
        role=UserRole.USER,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture
async def admin_user(session: AsyncSession) -> User:
    user = User(
        email="admin@example.com",
        hashed_password=hash_password("adminpass123"),
        display_name="Admin User",
        role=UserRole.ADMIN,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture
def user_token(test_user: User) -> str:
    return create_access_token(test_user.id, test_user.role)  # type: ignore[arg-type]


@pytest.fixture
def admin_token(admin_user: User) -> str:
    return create_access_token(admin_user.id, admin_user.role)  # type: ignore[arg-type]


@pytest.fixture
def auth_headers(user_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}
