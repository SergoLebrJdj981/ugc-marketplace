"""Chat messaging endpoints and WebSocket handlers."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import TokenError, get_subject, verify_token
from app.db.session import get_session
from app.models import Message, User
from app.schemas.chat import MessageListResponse, MessageRead, MessageSendRequest, MessageSendResponse
from app.services.chat import connection_manager, log_chat_event

router = APIRouter(prefix="/chat", tags=["Chat"])
ws_router = APIRouter()


def _serialize_message(message: Message) -> dict:
    schema = MessageRead.model_validate(message, from_attributes=True)
    return jsonable_encoder(schema, by_alias=True)


@router.post("/send", status_code=status.HTTP_201_CREATED, response_model=MessageSendResponse)
async def send_message(
    payload: MessageSendRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_session)],
):
    if payload.receiver_id is None or not payload.content or not payload.content.strip():
        log_chat_event(
            "message",
            sender_id=current_user.id,
            receiver_id=payload.receiver_id,
            chat_id=payload.chat_id,
            content=payload.content,
            error="missing receiver_id or content",
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="receiver_id и content обязательны")

    if payload.receiver_id == current_user.id:
        log_chat_event(
            "message",
            sender_id=current_user.id,
            receiver_id=payload.receiver_id,
            chat_id=payload.chat_id,
            content=payload.content,
            error="attempt to message self",
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя отправить сообщение самому себе")

    receiver = db.get(User, payload.receiver_id)
    if receiver is None:
        log_chat_event(
            "message",
            sender_id=current_user.id,
            receiver_id=payload.receiver_id,
            chat_id=payload.chat_id,
            content=payload.content,
            status="error",
            error="receiver not found",
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Получатель не найден")

    message = Message(
        chat_id=str(payload.chat_id),
        sender_id=current_user.id,
        receiver_id=payload.receiver_id,
        content=payload.content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    serialized = _serialize_message(message)
    await connection_manager.broadcast(payload.chat_id, serialized)

    log_chat_event(
        "message",
        sender_id=current_user.id,
        receiver_id=payload.receiver_id,
        chat_id=payload.chat_id,
        content=payload.content,
        status="success",
    )
    return MessageSendResponse(status="success", message_id=message.id, timestamp=message.created_at)


@router.get("/{chat_id}", status_code=status.HTTP_200_OK, response_model=MessageListResponse)
def get_chat_history(
    chat_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_session)],
):
    messages = (
        db.query(Message)
        .filter(Message.chat_id == str(chat_id))
        .order_by(Message.created_at.asc())
        .all()
    )

    if messages:
        is_participant = any(
            message.sender_id == current_user.id or message.receiver_id == current_user.id for message in messages
        )
        if not is_participant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к этому чату")

    updated = False
    for message in messages:
        if message.receiver_id == current_user.id and not message.is_read:
            message.is_read = True
            updated = True

    if updated:
        db.commit()

    serialized_items = [MessageRead.model_validate(msg, from_attributes=True) for msg in messages]
    return MessageListResponse(total=len(serialized_items), items=serialized_items)


@ws_router.websocket("/ws/chat/{chat_id}")
async def chat_websocket(websocket: WebSocket, chat_id: UUID) -> None:
    token = websocket.query_params.get("token")
    if not token:
        log_chat_event("ws", chat_id=chat_id, status="error", error="missing token")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        payload = verify_token(token, expected_type="access")
        user_id = UUID(str(get_subject(payload)))
    except (TokenError, ValueError):
        log_chat_event("ws", chat_id=chat_id, status="error", error="invalid token")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await connection_manager.connect(chat_id, websocket, user_id=user_id)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await connection_manager.disconnect(chat_id, websocket, user_id=user_id)
    except Exception:
        await connection_manager.disconnect(chat_id, websocket, user_id=user_id)
        log_chat_event("ws", sender_id=user_id, chat_id=chat_id, status="error", error="unexpected disconnect")
        raise
