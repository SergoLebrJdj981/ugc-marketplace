"""Recurring maintenance tasks for the event system."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Final

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import func

from app.core.config import PROJECT_ROOT
from app.db.session import SessionLocal
from app.models.event_log import EventLog
from app.services.event_logger import LOG_FILE

STATS_FILE: Final[Path] = PROJECT_ROOT.parent / "logs" / "event_stats.json"
STATS_FILE.parent.mkdir(parents=True, exist_ok=True)


def cleanup_event_logs(max_age_days: int = 30) -> None:
    """Delete old event log entries and trim the file log."""

    cutoff = datetime.utcnow() - timedelta(days=max_age_days)

    session = SessionLocal()
    try:
        session.query(EventLog).filter(EventLog.created_at < cutoff).delete(synchronize_session=False)
        session.commit()
    finally:
        session.close()

    if LOG_FILE.exists():
        lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
        # keep the latest 1000 entries to avoid unbounded growth
        keep = lines[-1000:]
        LOG_FILE.write_text("\n".join(keep) + ("\n" if keep else ""), encoding="utf-8")


def recalculate_event_statistics() -> None:
    """Aggregate event statistics and persist them to disk."""

    session = SessionLocal()
    try:
        total = session.query(func.count(EventLog.id)).scalar() or 0
        per_type = {
            event_type: count
            for event_type, count in session.query(EventLog.event_type, func.count(EventLog.id)).group_by(EventLog.event_type)
        }
    finally:
        session.close()

    data = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "total_events": int(total),
        "events_by_type": {key: int(value) for key, value in per_type.items()},
    }
    STATS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def register_jobs(scheduler: AsyncIOScheduler) -> None:
    """Attach cron jobs to the provided scheduler instance."""

    scheduler.add_job(cleanup_event_logs, CronTrigger(hour=3, minute=0), id="cleanup_event_logs", replace_existing=True)
    scheduler.add_job(
        recalculate_event_statistics,
        CronTrigger(minute=0),
        id="recalculate_event_statistics",
        replace_existing=True,
    )
    # run once at startup to ensure metrics file exists
    scheduler.add_job(
        recalculate_event_statistics,
        id="initial_event_stats",
        replace_existing=True,
        next_run_time=datetime.utcnow(),
    )
