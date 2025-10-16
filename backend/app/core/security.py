"""Security helpers for password hashing and JWT handling."""

from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Final
from uuid import UUID, uuid4

import jwt
from jwt import PyJWTError

from app.core.config import settings


_PASSWORD_SALT: Final[bytes] = os.getenv("API_PASSWORD_SALT", "ugc-salt").encode()
_ACCESS_SECRET: Final[str] = settings.secret_key
_REFRESH_SECRET: Final[str] = settings.refresh_secret_key
_ALGORITHM: Final[str] = settings.algorithm

_revoked_refresh_tokens: dict[str, datetime] = {}


def _cleanup_revoked() -> None:
    now = datetime.now(timezone.utc)
    expired = [token for token, exp in _revoked_refresh_tokens.items() if exp <= now]
    for token in expired:
        _revoked_refresh_tokens.pop(token, None)


def hash_password(password: str) -> str:
    """Return a salted SHA-256 hash for persistent storage."""

    digest = hashlib.sha256(_PASSWORD_SALT + password.encode("utf-8")).hexdigest()
    return digest


def verify_password(password: str, hashed_password: str) -> bool:
    """Safely compare a plaintext password with its hash."""

    candidate = hash_password(password)
    return hmac.compare_digest(candidate, hashed_password)


class TokenError(ValueError):
    """Raised when a token is invalid or expired."""


def _build_payload(data: dict[str, Any], expires_delta: timedelta, token_type: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    return {
        **data,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "jti": str(uuid4()),
    }


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token."""

    delta = expires_delta or timedelta(minutes=settings.access_token_expires_minutes)
    payload = _build_payload(data, delta, token_type="access")
    return jwt.encode(payload, _ACCESS_SECRET, algorithm=_ALGORITHM)


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT refresh token."""

    delta = expires_delta or timedelta(days=settings.refresh_token_expires_days)
    payload = _build_payload(data, delta, token_type="refresh")
    return jwt.encode(payload, _REFRESH_SECRET, algorithm=_ALGORITHM)


def revoke_refresh_token(token: str, payload: dict[str, Any] | None = None) -> None:
    """Blacklist a refresh token by recording its expiry."""

    _cleanup_revoked()
    if payload is None:
        try:
            payload = verify_token(token, expected_type="refresh")
        except TokenError:
            return
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    _revoked_refresh_tokens[token] = exp


def is_refresh_token_revoked(token: str) -> bool:
    """Return True if the refresh token has been blacklisted."""

    _cleanup_revoked()
    return token in _revoked_refresh_tokens


def verify_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    """Decode and validate a JWT, raising TokenError on failure."""

    secret = _ACCESS_SECRET if expected_type == "access" else _REFRESH_SECRET
    try:
        payload = jwt.decode(token, secret, algorithms=[_ALGORITHM])
    except PyJWTError as exc:  # pragma: no cover - library raises various subclasses
        raise TokenError("Invalid token") from exc

    if payload.get("type") != expected_type:
        raise TokenError("Token has wrong type")

    if expected_type == "refresh" and is_refresh_token_revoked(token):
        raise TokenError("Token revoked")

    return payload


def get_subject(payload: dict[str, Any]) -> UUID:
    """Return the token subject as UUID."""

    try:
        return UUID(str(payload["sub"]))
    except (KeyError, ValueError) as exc:
        raise TokenError("Invalid subject") from exc
