"""Notification REST and WebSocket endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import Notification, User
from app.schemas import (
    NotificationListResponse,
    NotificationMarkReadRequest,
    NotificationMarkReadResponse,
    NotificationRead,
    NotificationSendRequest,
    NotificationSendResponse,
)
from app.services.notifications import (
    connection_manager,
    create_notification,
    log_notification_event,
    mark_notifications_read,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])
ws_router = APIRouter()


@router.get("", response_model=NotificationListResponse, status_code=status.HTTP_200_OK)
async def list_notifications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_session)],
    user_id: UUID | None = None,
    unread_only: bool = False,
) -> NotificationListResponse:
    target_user_id = user_id or current_user.id
    if target_user_id != current_user.id and current_user.role not in {"admin", "superadmin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для просмотра уведомлений")

    query = db.query(Notification).filter(Notification.user_id == target_user_id)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))

    notifications = query.order_by(Notification.created_at.desc()).all()
    items = [NotificationRead.model_validate(notification) for notification in notifications]
    return NotificationListResponse(total=len(items), items=items)


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationMarkReadResponse,
    status_code=status.HTTP_200_OK,
)
def mark_notification_read(
    notification_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_session)],
) -> NotificationMarkReadResponse:
    request = NotificationMarkReadRequest(notification_ids=[notification_id])
    updated = mark_notifications_read(db, request, user_id=current_user.id)
    return NotificationMarkReadResponse(updated=updated)


@router.post(
    "/send",
    response_model=NotificationSendResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_system_notification(
    payload: NotificationSendRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_session)],
) -> NotificationSendResponse:
    if current_user.role not in {"admin", "superadmin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")

    notification = await create_notification(
        db,
        user_id=payload.user_id,
        notification_type=payload.type,
        title=payload.title,
        content=payload.content,
        related_id=payload.related_id,
    )
    return NotificationSendResponse(notification=notification)


@ws_router.websocket("/ws/notifications/{user_id}")
async def notifications_websocket(websocket: WebSocket, user_id: UUID) -> None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        from app.core.security import TokenError, get_subject, verify_token

        payload = verify_token(token, expected_type="access")
        current_user_id = UUID(str(get_subject(payload)))
    except (TokenError, ValueError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if current_user_id != user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await connection_manager.connect(user_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await connection_manager.disconnect(user_id, websocket)
    except Exception:
        await connection_manager.disconnect(user_id, websocket)
        log_notification_event(
            user_id=user_id,
            notification_type="ws",
            title="unexpected disconnect",
            status="error",
        )
        raise
