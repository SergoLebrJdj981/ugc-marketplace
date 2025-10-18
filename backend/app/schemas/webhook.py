"""Schemas for webhook payloads and responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import OrderStatus


class BankWebhookPayload(BaseModel):
    event: str
    payment_id: UUID | None = None
    payout_id: UUID | None = None
    status: str
    signature: str | None = None
    metadata: dict[str, Any] | None = None
    description: str | None = None


class OrderWebhookPayload(BaseModel):
    order_id: UUID
    status: OrderStatus
    message: str | None = None
    signature: str | None = None
    metadata: dict[str, Any] | None = None


class WebhookEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_type: str
    payload: dict[str, Any]
    signature: str | None = None
    created_at: datetime


class WebhookAckResponse(BaseModel):
    status: str = "accepted"
