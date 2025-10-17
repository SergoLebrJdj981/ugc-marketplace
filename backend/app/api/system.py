"""System endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models import EventLog

router = APIRouter(prefix="/system")


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/metrics", status_code=status.HTTP_200_OK)
def metrics(db: Annotated[Session, Depends(get_session)]):
    total_events = db.query(func.count(EventLog.id)).scalar() or 0
    per_type = {
        event_type: count
        for event_type, count in db.query(EventLog.event_type, func.count(EventLog.id)).group_by(EventLog.event_type)
    }
    latest = (
        db.query(EventLog)
        .order_by(EventLog.created_at.desc())
        .limit(5)
        .all()
    )
    recent = [
        {
            "id": entry.id,
            "event_type": entry.event_type,
            "status": entry.status,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
        }
        for entry in latest
    ]
    return {
        "total_events": int(total_events),
        "events_by_type": per_type,
        "recent_events": recent,
    }
