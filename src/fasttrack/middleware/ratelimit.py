import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

from fasttrack.config import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, **kwargs) -> None:  # noqa: ANN001, ANN003
        super().__init__(app, **kwargs)
        settings = get_settings()
        self.max_requests = settings.RATE_LIMIT_REQUESTS
        self.window = settings.RATE_LIMIT_WINDOW
        self._timestamps: dict[str, list[float]] = defaultdict(list)

    def _get_key(self, request: Request) -> str:
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
        client = request.client
        return f"ip:{client.host}" if client else "ip:unknown"

    def _clean_window(self, key: str, now: float) -> None:
        cutoff = now - self.window
        self._timestamps[key] = [t for t in self._timestamps[key] if t > cutoff]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in ("/docs", "/redoc", "/openapi.json", "/health"):
            return await call_next(request)

        key = self._get_key(request)
        now = time.time()
        self._clean_window(key, now)

        if len(self._timestamps[key]) >= self.max_requests:
            oldest = self._timestamps[key][0]
            retry_after = int(self.window - (now - oldest)) + 1
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"Retry-After": str(retry_after)},
            )

        self._timestamps[key].append(now)
        return await call_next(request)
