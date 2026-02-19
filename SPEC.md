# P06: fasttrack — Async REST API with FastAPI

**Catalog ID:** P06 | **Size:** M | **Language:** Python 3.14 / FastAPI 0.115
**Repo name:** `fasttrack`
**One-liner:** A production-grade async REST API with FastAPI — SQLModel ORM, JWT authentication with refresh tokens, role-based permissions, WebSocket notifications, background tasks, cursor-based pagination, rate limiting, and a comprehensive async test suite.

---

## Why This Stands Out

- **Async throughout** — every database query, HTTP handler, and background task uses `async`/`await` with aiosqlite, demonstrating real async Python proficiency
- **SQLModel ORM** — type-safe models that are simultaneously SQLAlchemy ORM models and Pydantic validation schemas, created by the FastAPI author himself
- **JWT with refresh tokens** — proper auth flow with short-lived access tokens, long-lived refresh tokens, token rotation, and revocation via database blocklist
- **Role-based access control** — dependency-injectable permission system with admin/user roles, resource ownership checks, and decorator-free authorization
- **WebSocket notifications** — real-time push notifications over WebSocket with connection management, heartbeat, and per-user channels
- **Cursor-based pagination** — opaque cursors instead of offset/limit, providing stable pagination that doesn't break when data changes
- **Rate limiting middleware** — sliding-window rate limiter per IP and per user with configurable limits and Redis-free in-memory storage
- **Alembic migrations** — proper schema versioning with auto-generated migrations, not `create_all()` shortcuts

---

## Architecture

```
fasttrack/
├── src/
│   └── fasttrack/
│       ├── __init__.py
│       ├── main.py              # FastAPI app factory, lifespan, middleware registration
│       ├── config.py            # Settings via pydantic-settings (env + .env file)
│       ├── database.py          # Async engine, session factory, base model
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py          # User model: email, hashed_password, role, is_active
│       │   ├── project.py       # Project model: name, description, owner_id, status
│       │   ├── task.py          # Task model: title, description, status, priority, assignee_id, project_id
│       │   └── comment.py       # Comment model: body, author_id, task_id, created_at
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── user.py          # User create/read/update schemas
│       │   ├── project.py       # Project create/read/update schemas
│       │   ├── task.py          # Task create/read/update schemas
│       │   ├── comment.py       # Comment create/read schemas
│       │   ├── auth.py          # Login request, token response, refresh request
│       │   └── pagination.py    # Cursor-based pagination response wrapper
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── auth.py          # POST /auth/login, /auth/refresh, /auth/logout
│       │   ├── users.py         # GET/PATCH /users, GET /users/me
│       │   ├── projects.py      # CRUD /projects with ownership checks
│       │   ├── tasks.py         # CRUD /projects/{id}/tasks with assignment
│       │   └── comments.py      # CRUD /tasks/{id}/comments
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── jwt.py           # JWT encode/decode, access + refresh token creation
│       │   ├── password.py      # bcrypt hash + verify
│       │   ├── dependencies.py  # get_current_user, require_role, require_owner
│       │   └── blocklist.py     # Token revocation blocklist (DB-backed)
│       ├── middleware/
│       │   ├── __init__.py
│       │   ├── ratelimit.py     # Sliding-window rate limiter middleware
│       │   └── cors.py          # CORS configuration
│       ├── websocket/
│       │   ├── __init__.py
│       │   ├── manager.py       # WebSocket connection manager (per-user channels)
│       │   └── handler.py       # WebSocket endpoint: connect, receive, broadcast
│       ├── tasks/
│       │   ├── __init__.py
│       │   └── background.py    # Background task functions (email, notifications)
│       └── utils/
│           ├── __init__.py
│           └── pagination.py    # Cursor encoding/decoding, paginated query builder
├── migrations/
│   ├── env.py                   # Alembic environment config (async)
│   ├── script.py.mako           # Migration template
│   └── versions/                # Auto-generated migration files
├── tests/
│   ├── conftest.py              # Fixtures: async client, test DB, auth headers, factories
│   ├── test_auth.py             # Login, refresh, logout, invalid credentials
│   ├── test_users.py            # User profile, list users, admin operations
│   ├── test_projects.py         # CRUD projects, ownership, pagination
│   ├── test_tasks.py            # CRUD tasks, assignment, status transitions
│   ├── test_comments.py         # CRUD comments, authorization
│   ├── test_websocket.py        # WebSocket connect, receive notifications
│   ├── test_ratelimit.py        # Rate limiter enforcement
│   └── test_pagination.py       # Cursor-based pagination correctness
├── alembic.ini                  # Alembic configuration
├── pyproject.toml               # Project metadata, dependencies, scripts
├── docker-compose.yml           # Development: app + SQLite volume
├── Dockerfile                   # Multi-stage build for production
├── .env.example                 # SECRET_KEY, DATABASE_URL, CORS_ORIGINS
├── .gitignore
├── .python-version              # 3.14
├── ruff.toml                    # Ruff linter config
├── LICENSE
└── README.md
```

---

## API Reference

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/login` | Login with email/password, receive access + refresh tokens | None |
| POST | `/auth/refresh` | Exchange refresh token for new token pair | Refresh token |
| POST | `/auth/logout` | Revoke current token pair | Access token |

### Users

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/users/me` | Get current user profile | User |
| PATCH | `/users/me` | Update current user profile | User |
| GET | `/users` | List all users (paginated) | Admin |
| GET | `/users/{id}` | Get user by ID | Admin |
| PATCH | `/users/{id}` | Update user (role, is_active) | Admin |

### Projects

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/projects` | Create a project | User |
| GET | `/projects` | List user's projects (paginated) | User |
| GET | `/projects/{id}` | Get project details | Owner |
| PATCH | `/projects/{id}` | Update project | Owner |
| DELETE | `/projects/{id}` | Delete project and tasks | Owner |

### Tasks

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/projects/{id}/tasks` | Create a task in project | Owner |
| GET | `/projects/{id}/tasks` | List project tasks (paginated, filterable) | Owner |
| GET | `/tasks/{id}` | Get task details | Owner/Assignee |
| PATCH | `/tasks/{id}` | Update task (status, assignee, priority) | Owner/Assignee |
| DELETE | `/tasks/{id}` | Delete task | Owner |

### Comments

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/tasks/{id}/comments` | Add comment to task | Owner/Assignee |
| GET | `/tasks/{id}/comments` | List task comments (paginated) | Owner/Assignee |
| DELETE | `/comments/{id}` | Delete comment | Author/Admin |

### WebSocket

| Endpoint | Description | Auth |
|----------|-------------|------|
| `ws://host/ws` | Real-time notifications (task assigned, comment added, status changed) | Token query param |

### Pagination Response

```json
{
  "items": [...],
  "next_cursor": "eyJpZCI6IDQyfQ==",
  "has_more": true
}
```

---

## Auth Flow

```
1. POST /auth/login  { email, password }
   → { access_token (15min), refresh_token (7d), token_type: "bearer" }

2. Requests: Authorization: Bearer <access_token>

3. POST /auth/refresh  { refresh_token }
   → { access_token (new, 15min), refresh_token (new, 7d) }
   Old refresh token is revoked (rotation)

4. POST /auth/logout
   → Both tokens added to blocklist
```

---

## WebSocket Protocol

```
1. Client connects: ws://host/ws?token=<access_token>
2. Server validates token, registers connection for user
3. Server sends notifications as JSON:
   { "type": "task_assigned", "data": { "task_id": 1, "project": "My Project" } }
   { "type": "comment_added", "data": { "task_id": 1, "author": "jane" } }
   { "type": "status_changed", "data": { "task_id": 1, "old": "todo", "new": "in_progress" } }
4. Server sends ping every 30s, client responds pong
5. Client disconnect → remove from manager
```

---

## Tech Stack

| Component | Choice |
|-----------|--------|
| Language | Python 3.14 |
| Framework | FastAPI 0.115 |
| ORM | SQLModel 0.0.22 (SQLAlchemy 2.0 + Pydantic v2) |
| Database | SQLite with aiosqlite (async driver) |
| Migrations | Alembic 1.14 (async mode) |
| Auth | python-jose (JWT), bcrypt (passwords) |
| Validation | Pydantic v2 (built into FastAPI) |
| WebSocket | FastAPI WebSocket (built-in, via Starlette) |
| Settings | pydantic-settings (env var loading) |
| Testing | pytest + pytest-asyncio + httpx (AsyncClient) |
| Containerization | Docker + Docker Compose |
| Linting | ruff |

---

## Phased Build Plan

### Phase 1: Foundation

**1.1 — Project setup**
- `pyproject.toml` with metadata, dependencies, scripts
- Directory structure, `ruff.toml`, `.gitignore`, `.python-version`
- Install: `fastapi[standard]`, `sqlmodel`, `aiosqlite`, `python-jose[cryptography]`, `bcrypt`, `pydantic-settings`, `alembic`, `httpx`, `pytest`, `pytest-asyncio`, `uvicorn`

**1.2 — Config + database**
- `Settings` class via pydantic-settings: `SECRET_KEY`, `DATABASE_URL`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `CORS_ORIGINS`
- Async SQLAlchemy engine with aiosqlite
- Async session factory with `async_sessionmaker`
- `.env.example` with all config keys
- Tests: settings load from env, database session creates/closes

**1.3 — SQLModel models**
- `User`: id, email (unique), hashed_password, display_name, role (admin/user), is_active, created_at, updated_at
- `Project`: id, name, description, status (active/archived), owner_id (FK→User), created_at, updated_at
- `Task`: id, title, description, status (todo/in_progress/done), priority (low/medium/high), project_id (FK→Project), assignee_id (FK→User, nullable), created_at, updated_at
- `Comment`: id, body, task_id (FK→Task), author_id (FK→User), created_at
- Alembic init with async env.py, generate initial migration
- Tests: models create/read/update in test DB

**1.4 — Pydantic schemas**
- Request/response schemas for each model (Create, Read, Update variants)
- `TokenResponse`, `LoginRequest`, `RefreshRequest` auth schemas
- `PaginatedResponse[T]` generic with items, next_cursor, has_more
- Tests: schema validation accepts valid, rejects invalid

### Phase 2: Authentication

**2.1 — Password hashing**
- bcrypt hash and verify functions
- Tests: hash is different from plain text, verify matches, verify rejects wrong password

**2.2 — JWT tokens**
- `create_access_token(user_id, role)` → JWT with 15min expiry
- `create_refresh_token(user_id)` → JWT with 7d expiry
- `decode_token(token)` → payload or raise
- Tests: encode/decode round-trip, expired token raises, invalid token raises

**2.3 — Token blocklist**
- `BlockedToken` model: jti (unique), blocked_at, expires_at
- `block_token(jti)`, `is_blocked(jti)` async functions
- Cleanup expired entries on app startup
- Tests: block and check, non-blocked passes, expired cleanup

**2.4 — Auth dependencies**
- `get_current_user` — extract token from Authorization header, decode, fetch user, check blocklist
- `require_role(role)` — dependency that checks user role
- `require_owner(resource)` — dependency that checks resource ownership
- Tests: valid token → user, expired → 401, wrong role → 403, non-owner → 403

**2.5 — Auth routes**
- `POST /auth/login` — validate credentials, return token pair
- `POST /auth/refresh` — validate refresh token, rotate (block old, issue new pair)
- `POST /auth/logout` — block both tokens
- Tests: login success/failure, refresh rotates tokens, logout revokes

### Phase 3: CRUD + Pagination

**3.1 — Cursor-based pagination**
- Encode cursor: base64 of `{"id": last_id}` (opaque to client)
- Decode cursor: extract last_id for `WHERE id > last_id`
- `paginate(query, cursor, limit)` → items + next_cursor + has_more
- Tests: first page no cursor, subsequent pages use cursor, empty page has_more=false

**3.2 — Project routes**
- Full CRUD with ownership checks
- List: paginated, filtered by owner (users see own projects, admin sees all)
- Tests: create, read, update, delete, unauthorized access blocked, pagination

**3.3 — Task routes**
- CRUD nested under projects (`/projects/{id}/tasks`)
- Assignment: set assignee_id, trigger WebSocket notification
- Status transitions: todo → in_progress → done
- Filter by status, priority, assignee
- Tests: CRUD, assignment, filters, unauthorized

**3.4 — Comment routes**
- CRUD nested under tasks (`/tasks/{id}/comments`)
- Only author or admin can delete
- Adding comment triggers WebSocket notification
- Tests: create, list, delete own, cannot delete others (non-admin)

### Phase 4: WebSocket + Background Tasks + Middleware

**4.1 — WebSocket connection manager**
- `ConnectionManager`: dict of user_id → set of WebSocket connections
- `connect(user_id, ws)`, `disconnect(user_id, ws)`, `send_to_user(user_id, message)`
- Token validation on connect (from query parameter)
- Heartbeat: ping every 30s, disconnect on pong timeout
- Tests: connect/disconnect, send to specific user, invalid token rejected

**4.2 — WebSocket notifications**
- Trigger notifications from route handlers: task assigned, comment added, status changed
- JSON message format: `{ type, data, timestamp }`
- Tests: assign task → assignee receives notification, add comment → task owner notified

**4.3 — Background tasks**
- Use FastAPI `BackgroundTasks` for non-blocking work
- Example: send notification email on task assignment (log-only, no real email)
- Example: update project statistics after task status change
- Tests: background task is enqueued and executes

**4.4 — Rate limiting middleware**
- Sliding-window algorithm: track request timestamps per IP (or per user if authenticated)
- Configurable: requests per window, window size
- Return `429 Too Many Requests` with `Retry-After` header
- Tests: within limit passes, exceeding limit returns 429, window slides

**4.5 — CORS middleware**
- Configurable origins from settings
- Tests: allowed origin passes, disallowed blocked

### Phase 5: Docker + Polish

**5.1 — Docker Compose**
- `Dockerfile`: multi-stage (builder + runtime), non-root user
- `docker-compose.yml`: app service with SQLite volume mount, env_file
- Tests: `docker compose build` succeeds

**5.2 — App factory + lifespan**
- `create_app()` factory function: register routers, middleware, WebSocket, lifespan
- Lifespan: create tables on startup (dev), cleanup blocklist, shutdown WebSocket manager
- Auto-generated OpenAPI docs at `/docs` and `/redoc`

**5.3 — Integration tests**
- Full user journey: register → login → create project → add tasks → assign → comment → check WebSocket
- Admin operations: list users, change roles
- Token refresh and rotation
- Rate limit enforcement

**5.4 — README and documentation**
- Badges, install, quick start
- API reference table
- Auth flow diagram
- WebSocket protocol description
- Docker Compose usage
- Development commands (test, lint, migrate)
- OpenAPI docs screenshot placeholder

---

## Commit Plan

1. `chore: scaffold project with pyproject.toml and directory structure`
2. `feat: add config with pydantic-settings and async database setup`
3. `feat: add SQLModel models for User, Project, Task, Comment`
4. `feat: add Alembic migrations with async support`
5. `feat: add Pydantic request/response schemas`
6. `feat: add password hashing and JWT token utilities`
7. `feat: add token blocklist for revocation`
8. `feat: add auth dependencies — get_current_user, require_role, require_owner`
9. `feat: add auth routes — login, refresh, logout`
10. `feat: add cursor-based pagination utility`
11. `feat: add project CRUD routes with ownership`
12. `feat: add task CRUD routes with assignment and filters`
13. `feat: add comment CRUD routes with authorization`
14. `feat: add WebSocket connection manager with heartbeat`
15. `feat: add WebSocket notification triggers`
16. `feat: add background tasks for notifications`
17. `feat: add sliding-window rate limiting middleware`
18. `feat: add CORS middleware configuration`
19. `feat: add app factory with lifespan and OpenAPI`
20. `feat: add Docker and Docker Compose configuration`
21. `test: add integration tests for full user journeys`
22. `docs: add README with API reference, auth flow, and setup guide`
