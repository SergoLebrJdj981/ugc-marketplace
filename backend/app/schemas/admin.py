"""Schemas for admin API."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import AdminLevel, CampaignStatus, UserRole


class AdminUserRoleUpdate(BaseModel):
    role: UserRole | None = None
    admin_level: AdminLevel | None = None
    permissions: dict | None = None


class AdminCampaignStatusUpdate(BaseModel):
    status: CampaignStatus = Field(..., description="New campaign status")


class StatisticsResponse(BaseModel):
    data: dict[str, Any]


class AdminExportResponse(BaseModel):
    content: str
    filename: str
