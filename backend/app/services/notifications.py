"""Notification creation, logging, WebSocket dispatch, and Telegram forwarding."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Any, DefaultDict, Iterable, Set
from uuid import UUID

from fastapi import BackgroundTasks, WebSocket
from fastapi.encoders import jsonable_encoder
from loguru import logger
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketState

from app.core.config import settings
from app.db.session import SessionLocal
from app.models import Notification, TelegramLink
from app.services.telegram import send_telegram_message
from app.schemas.notification import (
    NotificationMarkReadRequest,
    NotificationRead,
    NotificationSendRequest,
)

notifications_logger = logger.bind(channel="notifications")


def _timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def log_notification_event(
    *,
    user_id: UUID | str,
    notification_type: str,
    title: str,
    status: str,
    error: str | None = None,
) -> None:
    pieces = [
        f"[NOTIFY] [{_timestamp()}]",
        f"user={user_id}",
        f"type={notification_type}",
        f'title="{title}"',
        f"status={status}",
    ]
    if error:
        pieces.append(f"error={error}")
    notifications_logger.info(" ".join(pieces))


class NotificationConnectionManager:
    """Track notification subscribers via WebSocket connections."""

    def __init__(self) -> None:
        self._connections: DefaultDict[UUID, Set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[user_id].add(websocket)
        log_notification_event(user_id=user_id, notification_type="ws", title="connect", status="success")

    async def disconnect(self, user_id: UUID, websocket: WebSocket) -> None:
        async with self._lock:
            connections = self._connections.get(user_id)
            if connections and websocket in connections:
                connections.remove(websocket)
                if not connections:
                    self._connections.pop(user_id, None)
        log_notification_event(user_id=user_id, notification_type="ws", title="disconnect", status="success")

    async def broadcast(self, user_id: UUID, payload: dict[str, Any]) -> None:
        async with self._lock:
            connections = list(self._connections.get(user_id, set()))

        for websocket in connections:
            if websocket.application_state != WebSocketState.CONNECTED:
                await self.disconnect(user_id, websocket)
                continue
            try:
                await websocket.send_json({"event": "notification", "data": payload})
            except Exception:  # pragma: no cover - defensive close
                await self.disconnect(user_id, websocket)

    async def reset(self) -> None:
        async with self._lock:
            self._connections.clear()

    def reset_sync(self) -> None:
        self._connections.clear()


connection_manager = NotificationConnectionManager()

# Allow overriding in tests
SessionFactory = SessionLocal


async def _dispatch_telegram(notification: NotificationRead) -> str:
    session = SessionFactory()
    try:
        links = (
            session.query(TelegramLink)
            .filter(TelegramLink.user_id == notification.user_id, TelegramLink.is_active.is_(True))
            .all()
        )
        if not links:
            return "no_subscribers"

        if not settings.telegram_bot_token:
            log_notification_event(
                user_id=notification.user_id,
                notification_type=notification.type,
                title=notification.title,
                status="skipped",
                error="bot_disabled",
            )
            return "skipped"

        text = f"{notification.title}\n{notification.content}" if notification.content else notification.title
        statuses = []
        for link in links:
            result = await send_telegram_message(link.telegram_id, text)
            statuses.append(result)

        if all(result == "delivered" for result in statuses):
            return "delivered"
        if any(result == "delivered" for result in statuses):
            return "partial"
        return statuses[0] if statuses else "skipped"
    finally:
        session.close()


async def _notify_realtime(notification: NotificationRead, send_telegram: bool) -> None:
    payload = jsonable_encoder(notification.model_dump())
    await connection_manager.broadcast(notification.user_id, payload)
    status = "delivered"
    if send_telegram:
        tg_status = await _dispatch_telegram(notification)
        status = "delivered" if tg_status == "skipped" else tg_status
    log_notification_event(
        user_id=notification.user_id,
        notification_type=notification.type,
        title=notification.title,
        status=status,
    )


async def create_notification(
    db: Session,
    *,
    user_id: UUID,
    notification_type: str,
    title: str,
    content: str,
    related_id: str | None = None,
    send_telegram: bool = True,
) -> NotificationRead:
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        content=content,
        related_id=related_id,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    data = NotificationRead.model_validate(notification)
    await _notify_realtime(data, send_telegram=send_telegram)
    return data


def mark_notifications_read(db: Session, payload: NotificationMarkReadRequest, user_id: UUID) -> int:
    if not payload.notification_ids:
        return 0

    query = (
        db.query(Notification)
        .filter(Notification.id.in_(payload.notification_ids), Notification.user_id == user_id)
    )
    notifications = query.all()
    updated = 0
    for notification in notifications:
        if not notification.is_read:
            notification.is_read = True
            updated += 1

    if updated:
        db.commit()

    return updated


def _persist_notification_sync(payload: NotificationSendRequest) -> None:
    session = SessionFactory()
    try:
        notification = Notification(
            user_id=payload.user_id,
            type=payload.type,
            title=payload.title,
            content=payload.content,
            related_id=payload.related_id,
        )
        session.add(notification)
        session.commit()
        session.refresh(notification)
        data = NotificationRead.model_validate(notification)
        log_notification_event(
            user_id=data.user_id,
            notification_type=data.type,
            title=data.title,
            status="queued",
        )
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():  # pragma: no cover
            loop.create_task(_notify_realtime(data, send_telegram=True))
        else:
            asyncio.run(_notify_realtime(data, send_telegram=True))
    except Exception:  # pragma: no cover
        session.rollback()
        notifications_logger.exception("Failed to persist notification for user %s", payload.user_id)
    finally:
        session.close()


def schedule_notification(background_tasks: BackgroundTasks, payload: NotificationSendRequest) -> None:
    background_tasks.add_task(_persist_notification_sync, payload)


def schedule_batch_notifications(
    background_tasks: BackgroundTasks,
    notifications: Iterable[NotificationSendRequest],
) -> None:
    for payload in notifications:
        schedule_notification(background_tasks, payload)
