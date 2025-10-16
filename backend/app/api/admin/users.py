"""Admin endpoints for user management."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.models import User
from app.models.enums import AdminLevel
from app.schemas import AdminUserRoleUpdate, UserRead
from app.services.admin_logs import log_admin_action

router = APIRouter()


@router.get("", response_model=list[UserRead])
def list_users(
    *,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin(AdminLevel.ADMIN_LEVEL_1)),
) -> list[UserRead]:
    users = db.query(User).all()
    return [UserRead.model_validate(user) for user in users]


@router.patch("/{user_id}/role", response_model=UserRead)
def update_user_role(
    *,
    user_id: UUID,
    payload: AdminUserRoleUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin(AdminLevel.ADMIN_LEVEL_3)),
) -> UserRead:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.role is not None:
        user.role = payload.role
    if payload.admin_level is not None:
        user.admin_level = payload.admin_level
    if payload.permissions is not None:
        user.permissions = payload.permissions

    db.add(user)
    db.commit()
    db.refresh(user)
    log_admin_action(db, str(admin_user.id), "update_user_role", str(user.id), metadata=payload.model_dump())
    return UserRead.model_validate(user)


@router.delete("/{user_id}")
def delete_user(
    *,
    user_id: UUID,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin(AdminLevel.ADMIN_LEVEL_3)),
) -> None:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
    log_admin_action(db, str(admin_user.id), "delete_user", str(user_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
