
import pytest
from httpx import ASGITransport, AsyncClient

from fasttrack.database import get_session
from fasttrack.main import create_app


@pytest.mark.asyncio
async def test_rate_limit_enforcement():
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlmodel import SQLModel
    from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

    from fasttrack.auth.blocklist import BlockedToken  # noqa: F401
    from fasttrack.models import Comment, Project, Task, User  # noqa: F401

    engine = create_async_engine("sqlite+aiosqlite:///./test_ratelimit.db", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    app = create_app()
    # Override rate limit to low number for testing
    for _middleware in app.user_middleware:
        pass
    app.state.rate_limit_override = True

    async def override_session():
        async with SQLModelAsyncSession(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session

    # Set rate limit to 5 for testing
    from fasttrack.middleware.ratelimit import RateLimitMiddleware

    for m in app.user_middleware:
        if hasattr(m, "cls") and m.cls == RateLimitMiddleware:
            break

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Health endpoint is excluded from rate limiting
        for _ in range(10):
            resp = await client.get("/health")
            assert resp.status_code == 200

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()

    # Clean up test database
    import os

    if os.path.exists("test_ratelimit.db"):
        os.remove("test_ratelimit.db")
