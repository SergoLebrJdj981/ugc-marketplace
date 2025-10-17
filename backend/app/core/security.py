"""Minimal JWT utilities."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import jwt

from app.core.config import settings


def create_access_token(data: dict[str, Any], expires_minutes: int | None = None) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes or settings.access_token_expires_minutes)
    to_encode = {**data, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict[str, Any], expires_days: int | None = None) -> str:
    expire = datetime.utcnow() + timedelta(days=expires_days or settings.refresh_token_expires_days)
    to_encode = {**data, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.refresh_secret_key, algorithm=settings.algorithm)


def verify_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    payload = jwt.decode(
        token,
        settings.secret_key if expected_type == "access" else settings.refresh_secret_key,
        algorithms=[settings.algorithm],
    )
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("Invalid token type")
    return payload
