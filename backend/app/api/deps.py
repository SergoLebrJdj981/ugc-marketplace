"""Shared API dependencies."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import TokenError, get_subject, verify_token
from app.db.session import get_session
from app.models import User
from app.models.enums import AdminLevel

auth_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """Provide a database session to request scope."""

    yield from get_session()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(auth_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Resolve the currently authenticated user from the Authorization header."""

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials
    try:
        payload = verify_token(token, expected_type="access")
        user_id = get_subject(payload)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


_ADMIN_LEVEL_ORDER = {
    AdminLevel.NONE: 0,
    AdminLevel.ADMIN_LEVEL_1: 1,
    AdminLevel.ADMIN_LEVEL_2: 2,
    AdminLevel.ADMIN_LEVEL_3: 3,
}


def require_admin(min_level: AdminLevel = AdminLevel.ADMIN_LEVEL_1):
    def dependency(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        user_level_value = _ADMIN_LEVEL_ORDER.get(current_user.admin_level, 0)
        required_value = _ADMIN_LEVEL_ORDER.get(min_level, 0)
        if user_level_value < required_value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
        return current_user

    return dependency
