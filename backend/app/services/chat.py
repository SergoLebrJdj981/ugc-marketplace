"""In-memory connection manager for chat WebSocket sessions."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Any, DefaultDict, Set
from uuid import UUID

from fastapi import WebSocket
from loguru import logger
from starlette.websockets import WebSocketState

chat_logger = logger.bind(channel="chat")


def _normalise(value: UUID | str | None) -> str:
    if value is None:
        return "None"
    return str(value)


def log_chat_event(
    event_type: str,
    *,
    sender_id: UUID | str | None = None,
    receiver_id: UUID | str | None = None,
    chat_id: UUID | str | None = None,
    content: str | None = None,
    status: str | None = None,
    error: str | None = None,
    action: str | None = None,
) -> None:
    """Write a formatted chat/WebSocket event to the chat log."""

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    prefix = "[CHAT]" if event_type.lower() == "message" else "[WS]"
    segments: list[str] = [f"{prefix} [{timestamp}]"]

    if event_type.lower() == "message":
        sender = _normalise(sender_id)
        receiver = _normalise(receiver_id)
        base = f"sender={sender} → receiver={receiver}"
        if content is not None:
            base = f'{base}: "{content}"'
        segments.append(base)
    else:
        user = _normalise(sender_id) if sender_id is not None else None
        if user and action:
            segments.append(f"user={user} {action}")
        elif user:
            segments.append(f"user={user}")
        elif action:
            segments.append(action)
        if chat_id is not None:
            segments[-1] = f"{segments[-1]} to chat_id={_normalise(chat_id)}"
        elif sender_id is None and chat_id is not None:
            segments.append(f"chat_id={_normalise(chat_id)}")

    meta: list[str] = []
    if status:
        meta.append(f"status={status}")
    if error:
        meta.append(f"error={error}")
    if meta:
        segments.append(f"({', '.join(meta)})")

    chat_logger.info(" ".join(segments))


class ChatConnectionManager:
    """Track WebSocket connections grouped by chat identifier."""

    def __init__(self) -> None:
        self._connections: DefaultDict[UUID, Set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, chat_id: UUID, websocket: WebSocket, *, user_id: UUID | None = None) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[chat_id].add(websocket)
        log_chat_event("ws", sender_id=user_id, chat_id=chat_id, action="connected", status="success")

    async def disconnect(self, chat_id: UUID, websocket: WebSocket, *, user_id: UUID | None = None) -> None:
        async with self._lock:
            connections = self._connections.get(chat_id)
            if connections and websocket in connections:
                connections.remove(websocket)
                if not connections:
                    self._connections.pop(chat_id, None)
        log_chat_event("ws", sender_id=user_id, chat_id=chat_id, action="disconnected")

    async def broadcast(self, chat_id: UUID, message: dict[str, Any]) -> None:
        payload = {"event": "message", "data": message}
        async with self._lock:
            connections = list(self._connections.get(chat_id, set()))

        for websocket in connections:
            if websocket.application_state != WebSocketState.CONNECTED:
                await self.disconnect(chat_id, websocket)
                continue
            try:
                await websocket.send_json(payload)
            except Exception:  # pragma: no cover - defensive cleanup
                await self.disconnect(chat_id, websocket)

    async def reset(self) -> None:
        async with self._lock:
            self._connections.clear()

    def reset_sync(self) -> None:
        self._connections.clear()


connection_manager = ChatConnectionManager()
