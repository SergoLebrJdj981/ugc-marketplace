"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.db.session import get_session
from app.models import User
from app.schemas.user import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth")


def _user_to_dict(user: User) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
    }


@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == payload.email).one_or_none()
    if not user or not verify_password(payload.password, user.password):
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


@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=TokenResponse)
def refresh(payload: RefreshRequest):
    try:
        data = verify_token(payload.refresh_token, expected_type="refresh")
    except TokenError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    claims = {key: data[key] for key in ("sub", "role") if key in data}
    access = create_access_token(claims)
    refresh_token = create_refresh_token(claims)
    return {
        "access_token": access,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_role": claims.get("role", ""),
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout():
    return {"status": "ok"}


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
def register_user(data: RegisterRequest, db: Session = Depends(get_session)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    user = User(
        email=data.email,
        password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    claims = {"sub": str(user.id), "role": user.role}
    access_token = create_access_token(claims)
    refresh_token = create_refresh_token(claims)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_role": user.role,
        "user": _user_to_dict(user),
    }
