"""Authentication endpoints."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.deps import get_db
from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    get_subject,
    hash_password,
    revoke_refresh_token,
    verify_password,
    verify_token,
)
from app.models import User, UserRole
from app.models.enums import AdminLevel
from app.schemas import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserRead,
)

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """Register a new user account."""

    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    hashed = hash_password(payload.password)
    user = User(
        email=payload.email,
        hashed_password=hashed,
        full_name=payload.full_name,
        role=payload.role if isinstance(payload.role, UserRole) else UserRole(payload.role),
        admin_level=payload.admin_level if isinstance(payload.admin_level, AdminLevel) else AdminLevel(payload.admin_level),
        permissions=payload.permissions or {},
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:  # pragma: no cover - central handler
        db.rollback()
        raise exc
    db.refresh(user)
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Validate credentials and return a bearer token."""

    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    claims = {"sub": str(user.id), "role": user.role.value}
    access_token = create_access_token(claims)
    refresh_token = create_refresh_token(claims)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Issue new access/refresh tokens using a valid refresh token."""

    try:
        refresh_payload = verify_token(payload.refresh_token, expected_type="refresh")
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user_id = get_subject(refresh_payload)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # Rotate refresh token: revoke old and issue new pair
    revoke_refresh_token(payload.refresh_token, refresh_payload)

    claims = {"sub": str(user.id), "role": user.role.value}
    access_token = create_access_token(claims)
    refresh_token = create_refresh_token(claims)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest) -> Response:
    """Revoke a refresh token so it can no longer be used."""

    try:
        refresh_payload = verify_token(payload.refresh_token, expected_type="refresh")
    except TokenError:
        # Treat invalid tokens as already logged out to avoid leaking information
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    revoke_refresh_token(payload.refresh_token, refresh_payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
