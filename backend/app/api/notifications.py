"""Notification endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import Notification, User

router = APIRouter(prefix="/notifications")


class MarkReadRequest(BaseModel):
    notification_ids: list[UUID]


def _serialize(notification: Notification) -> dict:
    return {
        "id": str(notification.id),
        "user_id": str(notification.user_id),
        "type": notification.type,
        "message": notification.message,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
    }


@router.get("", status_code=status.HTTP_200_OK)
def list_notifications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_session)],
    user_id: UUID | None = None,
):
    target_user_id = user_id or current_user.id

    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == target_user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    items = [_serialize(notification) for notification in notifications]
    return {"total": len(items), "items": items}


@router.post("/mark-read", status_code=status.HTTP_200_OK)
def mark_read(
    payload: MarkReadRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_session)],
):
    if not payload.notification_ids:
        return {"updated": 0}

    notifications_query = (
        db.query(Notification)
        .filter(Notification.id.in_(payload.notification_ids), Notification.user_id == current_user.id)
    )
    notifications = notifications_query.all()

    updated = 0
    for notification in notifications:
        if not notification.is_read:
            notification.is_read = True
            updated += 1

    if updated:
        db.commit()

    return {"updated": updated}
