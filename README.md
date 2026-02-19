# fasttrack

Production-grade async REST API with FastAPI — SQLModel ORM, JWT authentication with refresh tokens, role-based permissions, WebSocket notifications, background tasks, cursor-based pagination, rate limiting, and a comprehensive async test suite.

## Tech Stack

| Component | Choice |
|-----------|--------|
| Language | Python 3.13 |
| Framework | FastAPI 0.115 |
| ORM | SQLModel (SQLAlchemy 2.0 + Pydantic v2) |
| Database | SQLite with aiosqlite (async) |
| Migrations | Alembic (async mode) |
| Auth | python-jose (JWT) + bcrypt |
| WebSocket | FastAPI built-in |
| Testing | pytest + pytest-asyncio + httpx |
| Linting | ruff |

## Prerequisites

- Python 3.12+
- pip

## Installation

```bash
git clone https://github.com/devaloi/fasttrack.git
cd fasttrack
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Configuration

Copy the example env file and customize:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `change-me-to-a-random-secret` | JWT signing key |
| `DATABASE_URL` | `sqlite+aiosqlite:///./fasttrack.db` | Database connection string |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |
| `RATE_LIMIT_REQUESTS` | `100` | Max requests per window |
| `RATE_LIMIT_WINDOW` | `60` | Rate limit window (seconds) |

## Quick Start

```bash
# Run the development server
uvicorn fasttrack.main:app --reload

# Open API docs
open http://localhost:8000/docs
```

## API Reference

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/register` | Register a new user | None |
| POST | `/api/v1/auth/login` | Login, receive token pair | None |
| POST | `/api/v1/auth/refresh` | Rotate refresh token | Refresh token |
| POST | `/api/v1/auth/logout` | Revoke current tokens | Access token |

### Users

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/users/me` | Current user profile | User |
| PATCH | `/api/v1/users/me` | Update profile | User |
| GET | `/api/v1/users` | List all users | Admin |
| GET | `/api/v1/users/{id}` | Get user by ID | Admin |
| PATCH | `/api/v1/users/{id}` | Update user | Admin |

### Projects

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/projects` | Create project | User |
| GET | `/api/v1/projects` | List user's projects | User |
| GET | `/api/v1/projects/{id}` | Get project | Owner |
| PATCH | `/api/v1/projects/{id}` | Update project | Owner |
| DELETE | `/api/v1/projects/{id}` | Delete project | Owner |

### Tasks

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/projects/{id}/tasks` | Create task | Owner |
| GET | `/api/v1/projects/{id}/tasks` | List tasks (filterable) | Owner |
| GET | `/api/v1/tasks/{id}` | Get task | Owner/Assignee |
| PATCH | `/api/v1/tasks/{id}` | Update task | Owner/Assignee |
| DELETE | `/api/v1/tasks/{id}` | Delete task | Owner |

### Comments

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/tasks/{id}/comments` | Add comment | Owner/Assignee |
| GET | `/api/v1/tasks/{id}/comments` | List comments | Owner/Assignee |
| DELETE | `/api/v1/comments/{id}` | Delete comment | Author/Admin |

### WebSocket

```
ws://localhost:8000/ws?token=<access_token>
```

Notifications: `task_assigned`, `comment_added`, `status_changed`

### Pagination

All list endpoints use cursor-based pagination:

```json
{
  "items": [...],
  "next_cursor": "eyJpZCI6IDQyfQ==",
  "has_more": true
}
```

Query params: `?cursor=<next_cursor>&limit=20`

## Auth Flow

```
1. POST /api/v1/auth/login  { email, password }
   → { access_token (15min), refresh_token (7d), token_type: "bearer" }

2. Requests: Authorization: Bearer <access_token>

3. POST /api/v1/auth/refresh  { refresh_token }
   → New token pair (old refresh token revoked)

4. POST /api/v1/auth/logout  → Token added to blocklist
```

## Development

```bash
# Run tests
python -m pytest

# Lint
ruff check .

# Format
ruff format .

# Run migrations
alembic upgrade head

# Generate migration
alembic revision --autogenerate -m "description"
```

## Docker

```bash
docker compose up --build
```

## License

MIT
