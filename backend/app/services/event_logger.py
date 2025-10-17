"""Event logging service."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import PROJECT_ROOT
from app.db.session import SessionLocal
from app.models.event_log import EventLog

LOG_FILE = PROJECT_ROOT.parent / "logs" / "events.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
STATS_FILE = LOG_FILE.parent / "event_stats.json"

SessionFactory = SessionLocal


def log_event(event_type: str, payload: dict, status: str = "ok", session: Session | None = None) -> EventLog:
    owns_session = session is None
    db = session or SessionFactory()
    try:
        entry = EventLog(event_type=event_type, payload=payload, status=status)
        db.add(entry)
        db.commit()
        db.refresh(entry)
    finally:
        if owns_session:
            db.close()

    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {
                    "id": entry.id,
                    "event_type": event_type,
                    "payload": payload,
                    "status": status,
                    "created_at": entry.created_at.isoformat() if entry.created_at else None,
                },
                default=str,
            )
            + "\n"
        )

    if owns_session:
        _update_statistics()

    return entry


def _update_statistics() -> None:
    session = SessionFactory()
    try:
        total = session.query(func.count(EventLog.id)).scalar() or 0
        by_type = {
            event_type: count
            for event_type, count in session.query(EventLog.event_type, func.count(EventLog.id)).group_by(EventLog.event_type)
        }
    finally:
        session.close()

    data = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "total_events": int(total),
        "events_by_type": {key: int(value) for key, value in by_type.items()},
    }
    STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
