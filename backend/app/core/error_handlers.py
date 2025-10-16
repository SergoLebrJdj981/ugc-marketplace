"""Application-level exception handlers."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from starlette import status

from app.core.security import TokenError


def _error_response(status_code: int, message: str, details: list[Any] | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "code": status_code,
            "message": message,
            "details": details or [],
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Bind shared exception handlers to the FastAPI instance."""

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
        logger.warning("IntegrityError at {path}: {error}", path=request.url.path, error=exc)
        return _error_response(status.HTTP_400_BAD_REQUEST, "Database constraint violation")

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.debug("Validation error on %s: %s", request.url.path, exc.errors())
        return _error_response(status.HTTP_400_BAD_REQUEST, "Invalid request", exc.errors())

    @app.exception_handler(ValidationError)
    async def handle_pydantic_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
        logger.debug("Pydantic validation error on %s: %s", request.url.path, exc.errors())
        return _error_response(status.HTTP_400_BAD_REQUEST, "Invalid data", exc.errors())

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        details = exc.detail if isinstance(exc.detail, list) else []
        message = exc.detail if isinstance(exc.detail, str) else exc.detail or "HTTP error"
        return _error_response(exc.status_code, message, details)

    @app.exception_handler(TokenError)
    async def handle_token_error(request: Request, exc: TokenError) -> JSONResponse:
        logger.warning("Token error on %s: %s", request.url.path, exc)
        return _error_response(status.HTTP_401_UNAUTHORIZED, str(exc))

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:  # pragma: no cover
        logger.exception("Unhandled exception at %s", request.url.path, exc_info=exc)
        return _error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "Unexpected server error")
