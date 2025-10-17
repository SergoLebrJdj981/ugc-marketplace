"""Admin endpoints."""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.db.session import get_session
from app.models import EventLog, Notification, User

router = APIRouter(prefix="/admin")


@router.get("/users")
def list_users(db: Session = Depends(get_session)):
    users = db.query(User).all()
    return [
        {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        }
        for user in users
    ]


@router.get("/statistics")
def statistics(db: Session = Depends(get_session)):
    user_count = db.query(func.count(User.id)).scalar() or 0
    notification_count = db.query(func.count(Notification.id)).scalar() or 0
    event_count = db.query(func.count(EventLog.id)).scalar() or 0
    return {
        "total_users": int(user_count),
        "total_notifications": int(notification_count),
        "total_events": int(event_count),
    }
