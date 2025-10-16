"""Pydantic schemas for orders."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.models.enums import OrderStatus


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: OrderStatus
    campaign_id: UUID
    creator_id: UUID
    brand_id: UUID
    agreed_budget: Decimal | None = None

    @field_serializer("agreed_budget")
    def serialize_budget(self, agreed_budget: Decimal | None) -> str | None:
        if agreed_budget is None:
            return None
        return f"{agreed_budget:.2f}"


class OrderListResponse(BaseModel):
    items: list[OrderRead]
    total: int


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
