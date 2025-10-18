"""Schemas for admin moderation workflows."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AdminActionType, AdminLevel, CampaignStatus


class ModerationUser(BaseModel):
    id: UUID
    email: str
    full_name: str | None = None
    role: str
    admin_level: AdminLevel
    is_active: bool
    status: Literal["active", "blocked"]
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ModerationUsersResponse(BaseModel):
    total: int
    items: list[ModerationUser]


class ModerationCampaign(BaseModel):
    id: UUID
    title: str
    status: CampaignStatus
    is_blocked: bool
    moderation_state: Literal["active", "blocked", "under_review"]
    brand_id: UUID
    brand_name: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ModerationCampaignsResponse(BaseModel):
    total: int
    items: list[ModerationCampaign]


class AdminActionRead(BaseModel):
    id: UUID
    admin_id: UUID
    target_id: UUID
    action_type: AdminActionType
    description: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ModerationToggleRequest(BaseModel):
    blocked: bool = Field(..., description="True — заблокировать, False — снять блокировку")
    reason: str | None = Field(default=None, description="Комментарий администратора")


class ModerationWarningRequest(BaseModel):
    user_id: UUID
    message: str = Field(..., min_length=1, max_length=500)


class ModerationUserActionResponse(BaseModel):
    user: ModerationUser
    action: AdminActionRead


class ModerationCampaignActionResponse(BaseModel):
    campaign: ModerationCampaign
    action: AdminActionRead


class ModerationWarningResponse(BaseModel):
    user: ModerationUser
    action: AdminActionRead


class ModerationLogsResponse(BaseModel):
    total: int
    items: list[AdminActionRead]
