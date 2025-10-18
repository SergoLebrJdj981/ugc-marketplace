"""Pydantic schemas for notifications."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    type: str
    title: str
    content: str
    related_id: str | None = None
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    items: list[NotificationRead]
    total: int


class NotificationMarkReadRequest(BaseModel):
    notification_ids: list[UUID]


class NotificationMarkReadResponse(BaseModel):
    updated: int


class NotificationSendRequest(BaseModel):
    user_id: UUID
    type: str
    title: str
    content: str
    related_id: str | None = None


class NotificationSendResponse(BaseModel):
    notification: NotificationRead
