"""Helpers for scheduling notifications via FastAPI background tasks."""

from __future__ import annotations

import logging
from typing import Iterable
from uuid import UUID

from fastapi import BackgroundTasks

from app.db.session import SessionLocal
from app.models import Notification

logger = logging.getLogger("ugc.notifications")

# Allow overriding in tests
SessionFactory = SessionLocal


def _persist_notification(user_id: UUID, notification_type: str, message: str) -> None:
    session = SessionFactory()
    try:
        notification = Notification(user_id=user_id, type=notification_type, message=message)
        session.add(notification)
        session.commit()
    except Exception as exc:  # pragma: no cover - logged centrally
        session.rollback()
        logger.exception("Failed to persist notification for user %s", user_id, exc_info=exc)
    finally:
        session.close()


def schedule_notification(background_tasks: BackgroundTasks, *, user_id: UUID, notification_type: str, message: str) -> None:
    """Queue a notification creation in the background."""

    background_tasks.add_task(_persist_notification, user_id, notification_type, message)


def schedule_batch_notifications(
    background_tasks: BackgroundTasks,
    notifications: Iterable[tuple[UUID, str, str]],
) -> None:
    """Queue multiple notifications in a single helper call."""

    for user_id, notification_type, message in notifications:
        schedule_notification(background_tasks, user_id=user_id, notification_type=notification_type, message=message)
