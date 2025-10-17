"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.security import TokenError, create_access_token, create_refresh_token, verify_token
from app.db.session import get_session
from app.models import User

router = APIRouter(prefix="/auth")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


def _user_to_dict(user: User) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
    }


@router.post("/login", status_code=status.HTTP_200_OK)
def login(payload: LoginRequest, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == payload.email).one_or_none()
    if not user or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    claims = {"sub": str(user.id), "role": user.role}
    access = create_access_token(claims)
    refresh = create_refresh_token(claims)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "user_role": user.role,
        "user": _user_to_dict(user),
    }


@router.post("/refresh", status_code=status.HTTP_200_OK)
def refresh(payload: RefreshRequest):
    try:
        data = verify_token(payload.refresh_token, expected_type="refresh")
    except TokenError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    claims = {key: data[key] for key in ("sub", "role") if key in data}
    access = create_access_token(claims)
    refresh_token = create_refresh_token(claims)
    return {"access_token": access, "refresh_token": refresh_token, "token_type": "bearer", "user_role": claims.get("role")}


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout():
    return {"status": "ok"}
