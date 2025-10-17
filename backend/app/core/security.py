"""Minimal JWT utilities."""

from __future__ import annotations

import hmac
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt
from passlib.context import CryptContext

try:  # pragma: no cover - environment compatibility shim
    import bcrypt as _bcrypt

    if not hasattr(_bcrypt, "__about__"):
        class _About:
            __version__ = getattr(_bcrypt, "__version__", "")


        _bcrypt.__about__ = _About()  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover
    _bcrypt = None

from app.core.config import settings


class TokenError(Exception):
    """Raised when token validation fails."""


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str | None) -> str:
    """Hash a plain password using bcrypt (safe up to 72 bytes, UTF-8 aware)."""
    if not password:
        raise ValueError("Password cannot be empty")

    # Преобразуем в bytes для подсчёта длины в байтах
    if isinstance(password, str):
        password_bytes = password.encode("utf-8", errors="ignore")
    else:
        password_bytes = password

    # bcrypt принимает максимум 72 байта
    safe_password = password_bytes[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(safe_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash (UTF-8 safe, legacy compatible)."""
    if not plain_password or not hashed_password:
        return False
    try:
        password_bytes = plain_password.encode("utf-8", errors="ignore")
        return pwd_context.verify(password_bytes[:72].decode("utf-8", errors="ignore"), hashed_password)
    except Exception:
        return hmac.compare_digest(plain_password[:72], hashed_password)


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
