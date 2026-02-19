import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fasttrack.auth.blocklist import BlockedToken  # noqa: F401
from fasttrack.database import create_db_and_tables
from fasttrack.middleware.cors import add_cors_middleware
from fasttrack.middleware.ratelimit import RateLimitMiddleware
from fasttrack.models import Comment, Project, Task, User  # noqa: F401
from fasttrack.routers import auth, comments, projects, tasks, users
from fasttrack.websocket.handler import router as ws_router
from fasttrack.websocket.manager import manager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting up fasttrack API")
    await create_db_and_tables()
    yield
    logger.info("Shutting down fasttrack API")
    await manager.shutdown()


def create_app() -> FastAPI:
    app = FastAPI(
        title="fasttrack",
        description="Production-grade async REST API with FastAPI",
        version="0.1.0",
        lifespan=lifespan,
    )

    add_cors_middleware(app)
    app.add_middleware(RateLimitMiddleware)

    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(projects.router, prefix="/api/v1")
    app.include_router(tasks.router, prefix="/api/v1")
    app.include_router(comments.router, prefix="/api/v1")
    app.include_router(ws_router)

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run("fasttrack.main:app", host="0.0.0.0", port=8000, reload=True)
