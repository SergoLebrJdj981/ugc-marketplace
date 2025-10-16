"""Security helpers for password hashing and token generation."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta
from typing import Final


_TOKEN_SECRET: Final[bytes] = os.getenv("API_TOKEN_SECRET", "ugc-secret").encode()


def hash_password(password: str) -> str:
    """Return a salted SHA-256 hash for persistent storage."""
    salt = os.getenv("API_PASSWORD_SALT", "ugc-salt").encode()
    digest = hashlib.sha256(salt + password.encode("utf-8")).hexdigest()
    return digest


def verify_password(password: str, hashed_password: str) -> bool:
    """Safely compare a plaintext password with its hash."""
    candidate = hash_password(password)
    return hmac.compare_digest(candidate, hashed_password)


def create_access_token(subject: str, expires_minutes: int = 60) -> str:
    """Issue a mock JWT compatible token (base64 encoded claims)."""
    expiry = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = f"{subject}:{int(expiry.timestamp())}".encode("utf-8")
    signature = hmac.new(_TOKEN_SECRET, payload, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(payload + b"." + signature).decode("utf-8")
