"""Pydantic schemas for payments."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.models.enums import PaymentStatus, PaymentType


class PaymentCreate(BaseModel):
    order_id: UUID
    payment_type: PaymentType = PaymentType.HOLD
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=8, default="RUB")
    reference: str | None = Field(default=None, max_length=120)


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    payment_type: PaymentType
    status: PaymentStatus
    amount: Decimal
    currency: str
    created_at: datetime

    @field_serializer("amount")
    def serialize_amount(self, amount: Decimal) -> str:
        return f"{amount:.2f}"
