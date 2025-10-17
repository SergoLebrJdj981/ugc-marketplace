"""Custom middleware stack for logging and request safeguards."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict

from fastapi import FastAPI
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings
from app.core.metrics import record_error, record_request
from app.core.security import TokenError, get_subject, verify_token

request_logger = logger.bind(channel="request")
error_logger = logger.bind(channel="error")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Persist request/response data to log files."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.time()
        record_request()
        try:
            response = await call_next(request)
        except Exception as exc:  # pragma: no cover
            duration = (time.time() - start) * 1000
            record_error()
            error_logger.opt(exception=True).error(
                "%s %s -> ERROR (%0.2f ms): %s", request.method, request.url.path, duration, exc
            )
            raise
        duration = (time.time() - start) * 1000
        request_logger.info("%s %s -> %s (%0.2f ms)", request.method, request.url.path, response.status_code, duration)
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory IP based rate limiter used for local development."""

    def __init__(self, app: FastAPI, limit: int, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.limit = max(limit, 1)
        self.window_seconds = window_seconds
        self._reservoir: dict[str, tuple[int, float]] = defaultdict(lambda: (0, 0.0))
        self._lock = asyncio.Lock()
        global _rate_limiter_instance
        _rate_limiter_instance = self

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        async with self._lock:
            count, reset_ts = self._reservoir[client_ip]
            now = time.time()
            if reset_ts <= now:
                count, reset_ts = 0, now + self.window_seconds
            count += 1
            self._reservoir[client_ip] = (count, reset_ts)
            if count > self.limit:
                retry_after = max(int(reset_ts - now), 1)
                error_logger.warning("Rate limit exceeded for %s", client_ip)
                return JSONResponse(
                    status_code=429,
                    headers={"Retry-After": str(retry_after)},
                    content={"detail": "Too many requests"},
                )
        return await call_next(request)

    async def reset(self) -> None:
        async with self._lock:
            self._reservoir.clear()

    def reset_sync(self) -> None:
        self._reservoir.clear()


_rate_limiter_instance: RateLimitMiddleware | None = None


async def reset_rate_limiter() -> None:
    if _rate_limiter_instance is not None:
        await _rate_limiter_instance.reset()


def reset_rate_limiter_sync() -> None:
    if _rate_limiter_instance is not None:
        _rate_limiter_instance.reset_sync()


class AdminActionMiddleware(BaseHTTPMiddleware):
    """Log admin API interactions to help with auditing."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        if request.url.path.startswith("/api/admin"):
            admin_id = "anonymous"
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.lower().startswith("bearer "):
                token = auth_header.split(" ", 1)[1]
                try:
                    payload = verify_token(token, expected_type="access")
                    admin_id = str(get_subject(payload))
                except TokenError:
                    admin_id = "invalid-token"
            request_logger.info(
                "admin_action %s %s -> %s (admin_id=%s)",
                request.method,
                request.url.path,
                response.status_code,
                admin_id,
            )
        return response


def _resolve_rate_limit() -> int:
    return getattr(settings, "rate_limit_per_minute", 60)


def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(RateLimitMiddleware, limit=_resolve_rate_limit())
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(AdminActionMiddleware)
