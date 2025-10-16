"""Pydantic schemas for campaign operations."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.models.enums import CampaignStatus


class CampaignCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = None
    budget: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=8, default="RUB")
    brand_id: UUID


class CampaignRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None = None
    status: CampaignStatus
    budget: Decimal
    currency: str
    brand_id: UUID
    created_at: datetime

    @field_serializer("budget")
    def serialize_budget(self, budget: Decimal) -> str:
        return f"{budget:.2f}"


class CampaignListResponse(BaseModel):
    items: list[CampaignRead]
    total: int
