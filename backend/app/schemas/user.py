"""Pydantic schemas for user and auth endpoints."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "creator"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_role: str
    user: Optional[dict] = None


class RefreshRequest(BaseModel):
    refresh_token: str
