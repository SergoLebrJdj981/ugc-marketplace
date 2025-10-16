"""Custom middleware stack for security and observability."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict

from fastapi import FastAPI
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings
from app.core.security import TokenError, get_subject, verify_token


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Log basic request/response information."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.time()
        response = await call_next(request)
        duration = (time.time() - start) * 1000
        client_ip = request.client.host if request.client else "unknown"
        logger.info(
            "[REQUEST] {method} {path} from {ip} -> {status} ({duration:.2f} ms)",
            method=request.method,
            path=request.url.path,
            ip=client_ip,
            status=response.status_code,
            duration=duration,
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter keyed by client IP."""

    def __init__(self, app: FastAPI, limit: int, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.limit = limit
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
                logger.warning("Rate limit exceeded for %s", client_ip)
                return JSONResponse(  # type: ignore[return-value]
                    status_code=429,
                    headers={"Retry-After": str(retry_after)},
                    content={
                        "status": "error",
                        "code": 429,
                        "message": "Too many requests",
                        "details": [],
                    },
                )

        return await call_next(request)

    async def reset(self) -> None:
        async with self._lock:
            self._reservoir.clear()

    def reset_sync(self) -> None:
        self._reservoir.clear()


# Expose a singleton middleware instance store for tests to reset
_rate_limiter_instance: RateLimitMiddleware | None = None


async def reset_rate_limiter() -> None:
    if _rate_limiter_instance is not None:
        await _rate_limiter_instance.reset()


def reset_rate_limiter_sync() -> None:
    if _rate_limiter_instance is not None:
        _rate_limiter_instance.reset_sync()


class AdminActionMiddleware(BaseHTTPMiddleware):
    """Write admin requests to a dedicated log."""

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
                except TokenError:  # pragma: no cover - logging best effort
                    admin_id = "invalid-token"

            logger.bind(admin_action=True).info(
                "admin_action method={method} path={path} status={status} admin_id={admin}",
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                admin=admin_id,
            )
        return response


def setup_middleware(app: FastAPI) -> None:
    """Configure middleware stack on the FastAPI application."""

    log_path = settings.log_path
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_path,
        rotation="10 MB",
        retention="14 days",
        format="[{time:YYYY-MM-DD HH:mm:ss}] {level} — {message}",
        enqueue=True,
    )

    admin_log_path = settings.log_path.parent / "admin_actions.log"
    admin_log_path.parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        admin_log_path,
        rotation="5 MB",
        retention="30 days",
        format="[{time:YYYY-MM-DD HH:mm:ss}] {level} — {message}",
        enqueue=True,
        filter=lambda record: record["extra"].get("admin_action") is True,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RateLimitMiddleware, limit=settings.rate_limit_per_minute)
    app.add_middleware(RequestLoggerMiddleware)
    app.add_middleware(AdminActionMiddleware)
