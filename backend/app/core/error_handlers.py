"""Application-level exception handlers."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette import status

logger = logging.getLogger("ugc.api")


def register_exception_handlers(app: FastAPI) -> None:
    """Bind shared exception handlers to the FastAPI instance."""

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
        logger.warning("IntegrityError: %s %s", request.url.path, exc.orig if exc.orig else exc)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Database constraint violation", "code": "integrity_error"},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:  # pragma: no cover
        logger.exception("Unhandled exception at %s", request.url.path, exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Unexpected server error", "code": "internal_error"},
        )
