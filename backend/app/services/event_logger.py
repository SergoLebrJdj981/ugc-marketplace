"""Event logging service."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.event_log import EventLog
from app.core.config import PROJECT_ROOT

LOG_FILE = PROJECT_ROOT.parent / "logs" / "events.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def log_event(event_type: str, payload: dict, status: str = "ok", session: Session | None = None) -> EventLog:
    owns_session = session is None
    db = session or SessionLocal()
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

    return entry
