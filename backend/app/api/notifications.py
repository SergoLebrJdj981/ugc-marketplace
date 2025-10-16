"""Notification endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_db
from app.models import Notification, User
from app.schemas import (
    NotificationListResponse,
    NotificationMarkReadRequest,
    NotificationMarkReadResponse,
    NotificationRead,
)

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


@router.post("/mark-read", response_model=NotificationMarkReadResponse)
def mark_notifications_read(
    *,
    db: SessionDep,
    payload: NotificationMarkReadRequest,
) -> NotificationMarkReadResponse:
    """Mark notifications as read."""

    if not payload.notification_ids:
        return NotificationMarkReadResponse(updated=0)

    stmt = select(Notification).where(Notification.id.in_(payload.notification_ids))
    notifications = list(db.scalars(stmt).all())
    for notification in notifications:
        notification.is_read = True
        db.add(notification)

    db.commit()
    return NotificationMarkReadResponse(updated=len(notifications))
