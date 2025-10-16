"""Notification endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_db
from app.models import Notification, User
from app.schemas import NotificationListResponse, NotificationRead

router = APIRouter(prefix="/notifications")

SessionDep = Annotated[Session, Depends(get_db)]


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    *,
    db: SessionDep,
    user_id: UUID | None = None,
    is_read: bool | None = Query(default=None),
) -> NotificationListResponse:
    """Return notifications with optional filtering."""

    stmt: Select[tuple[Notification]] = select(Notification).order_by(Notification.created_at.desc())
    if user_id:
        user_exists = db.get(User, user_id)
        if not user_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        stmt = stmt.where(Notification.user_id == user_id)
    if is_read is not None:
        stmt = stmt.where(Notification.is_read == is_read)

    items = list(db.scalars(stmt).all())
    return NotificationListResponse(items=[NotificationRead.model_validate(item) for item in items], total=len(items))
