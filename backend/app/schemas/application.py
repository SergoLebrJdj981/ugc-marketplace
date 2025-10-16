"""Pydantic schemas for applications."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.models.enums import ApplicationStatus


class ApplicationCreate(BaseModel):
    campaign_id: UUID
    creator_id: UUID
    pitch: str | None = Field(default=None, max_length=2000)
    proposed_budget: Decimal | None = Field(default=None, gt=0)
    message: str | None = None


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    campaign_id: UUID
    creator_id: UUID
    status: ApplicationStatus
    proposed_budget: Decimal | None = None
    created_at: datetime

    @field_serializer("proposed_budget")
    def serialize_budget(self, proposed_budget: Decimal | None) -> str | None:
        if proposed_budget is None:
            return None
        return f"{proposed_budget:.2f}"
