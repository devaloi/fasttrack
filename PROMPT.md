# Build fasttrack — Async REST API with FastAPI

You are building a **portfolio project** for a Senior AI Engineer's public GitHub. It must be impressive, clean, and production-grade. Read these docs before writing any code:

1. **`P06-fastapi-async-api.md`** — Complete project spec: architecture, API reference, auth flow, WebSocket protocol, SQLModel models, cursor-based pagination, rate limiting, phased build plan, commit plan. This is your primary blueprint. Follow it phase by phase.
2. **`github-portfolio.md`** — Portfolio goals and Definition of Done (Level 1 + Level 2). Understand the quality bar.
3. **`github-portfolio-checklist.md`** — Pre-publish checklist. Every item must pass before you're done.

---

## Instructions

### Read first, build second
Read all three docs completely before writing a single line of code. Understand the async architecture with aiosqlite, the SQLModel pattern (one model = ORM + schema), the JWT auth flow with token rotation and blocklist, the WebSocket connection manager with heartbeat, the cursor-based pagination approach, and the sliding-window rate limiter.

### Follow the phases in order
The project spec has 5 phases. Do them in order:
1. **Foundation** — project setup, pydantic-settings config, async database with aiosqlite, SQLModel models (User, Project, Task, Comment), Alembic migrations, Pydantic schemas
2. **Authentication** — bcrypt password hashing, JWT access + refresh tokens, token blocklist, auth dependencies (get_current_user, require_role, require_owner), auth routes
3. **CRUD + Pagination** — cursor-based pagination utility, project CRUD with ownership, task CRUD with assignment and filters, comment CRUD with authorization
4. **WebSocket + Background Tasks + Middleware** — WebSocket connection manager with heartbeat, notification triggers, background tasks, sliding-window rate limiter, CORS
5. **Docker + Polish** — Dockerfile + Docker Compose, app factory with lifespan, integration tests, README

### Commit frequently
Follow the commit plan in the spec. Use **conventional commits** (`feat:`, `test:`, `refactor:`, `docs:`, `chore:`). Each commit should be a logical unit.

### Quality non-negotiables
- **Fully async.** Every database call uses `async`/`await`. Use `aiosqlite` as the async SQLite driver. Use `async_sessionmaker` for session creation. Never block the event loop.
- **SQLModel everywhere.** Models serve as both SQLAlchemy ORM models and Pydantic schemas. Use `SQLModel` base class with `table=True` for database models and without for schemas. Leverage type annotations for automatic validation.
- **JWT with rotation.** Access tokens expire in 15 minutes, refresh tokens in 7 days. Refresh endpoint issues a new pair and revokes the old refresh token. Logout revokes both tokens via the blocklist.
- **Dependency-injectable auth.** `get_current_user`, `require_role`, and `require_owner` are FastAPI dependencies — clean, composable, testable. No decorator-based auth.
- **Cursor-based pagination.** Opaque base64-encoded cursors. Clients pass `cursor` query param, receive `next_cursor` + `has_more`. No offset/limit — stable pagination under concurrent writes.
- **WebSocket with heartbeat.** Connection manager tracks per-user connections. Server pings every 30 seconds. Notifications pushed on task assignment, comments, and status changes.
- **Rate limiting without Redis.** Sliding-window algorithm with in-memory storage. Per-IP for unauthenticated, per-user for authenticated. Returns 429 with `Retry-After` header.
- **Alembic migrations.** Async-compatible env.py. Auto-generate migrations from model changes. No `create_all()` in production code.
- **Tests with httpx AsyncClient.** All API tests use `httpx.AsyncClient` as the async test client. Factory fixtures for creating test users, projects, tasks. Isolated test database per test session.
- **Lint clean.** `ruff check` and `ruff format --check` must pass with zero issues.

### What NOT to do
- Don't use synchronous database calls. Everything must be async — `await session.execute()`, not `session.execute()`.
- Don't use offset-based pagination. Cursor-based is required for stability and performance.
- Don't store JWT tokens in the database for validation. Use stateless JWT with a blocklist only for revoked tokens.
- Don't use `requests` for testing. Use `httpx.AsyncClient` with `ASGITransport` — no real HTTP server needed in tests.
- Don't skip WebSocket heartbeat. Stale connections must be detected and cleaned up.
- Don't leave `# TODO` or `# FIXME` comments anywhere.

---

## GitHub Username

The GitHub username is **devaloi**. The repository is `github.com/devaloi/fasttrack`. Python package name is `fasttrack`.

## Start

Read the three docs. Then begin Phase 1 from `P06-fastapi-async-api.md`.
