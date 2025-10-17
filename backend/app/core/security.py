"""Minimal JWT utilities."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt

from app.core.config import settings


class TokenError(Exception):
    """Raised when token validation fails."""


def _build_token(
    data: dict[str, Any],
    *,
    expires_delta: timedelta | None,
    secret: str,
    token_type: str,
) -> str:
    """Create a signed JWT with standard claims."""
    lifetime = expires_delta or (
        timedelta(minutes=settings.access_token_expires_minutes)
        if token_type == "access"
        else timedelta(days=settings.refresh_token_expires_days)
    )
    now = datetime.now(timezone.utc)
    payload = {
        **data,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + lifetime).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm=settings.algorithm)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Generate a short-lived access token."""
    return _build_token(data, expires_delta=expires_delta, secret=settings.secret_key, token_type="access")


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Generate a long-lived refresh token."""
    return _build_token(
        data,
        expires_delta=expires_delta,
        secret=settings.refresh_secret_key,
        token_type="refresh",
    )


def verify_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    """Decode a JWT and optionally assert its type."""
    secrets: list[tuple[str, str]] = [
        (settings.secret_key, "access"),
        (settings.refresh_secret_key, "refresh"),
    ]
    if expected_type is not None:
        secrets = [pair for pair in secrets if pair[1] == expected_type]

    last_error: Exception | None = None
    for secret, token_type in secrets:
        try:
            payload = jwt.decode(token, secret, algorithms=[settings.algorithm])
        except jwt.PyJWTError as exc:  # pragma: no cover
            last_error = exc
            continue

        if payload.get("type") != token_type:
            raise TokenError("Invalid token type")
        return payload

    raise TokenError("Token validation failed") from last_error


def get_subject(payload: dict[str, Any]) -> UUID:
    """Extract the subject claim as UUID."""
    subject = payload.get("sub")
    if subject is None:
        raise TokenError("Missing subject claim")
    try:
        return UUID(str(subject))
    except ValueError as exc:
        raise TokenError("Invalid subject claim") from exc
