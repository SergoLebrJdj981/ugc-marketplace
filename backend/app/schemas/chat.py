"""Pydantic schemas for chat messaging."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, constr


class MessageSendRequest(BaseModel):
    """Payload for sending a chat message."""

    chat_id: UUID
    receiver_id: UUID
    content: constr(min_length=1, max_length=5000)  # type: ignore[valid-type]


class MessageRead(BaseModel):
    """Representation of a stored chat message."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    chat_id: UUID
    sender_id: UUID
    receiver_id: UUID
    content: str
    is_read: bool
    timestamp: datetime = Field(alias="created_at")


class MessageListResponse(BaseModel):
    """Collection of chat messages."""

    total: int
    items: list[MessageRead]


class MessageSendResponse(BaseModel):
    """Response returned after a chat message is persisted."""

    status: str
    message_id: UUID
    timestamp: datetime
