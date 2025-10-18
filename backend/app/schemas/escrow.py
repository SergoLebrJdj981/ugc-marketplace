"""Pydantic schemas for escrow operations."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import PaymentStatus, PayoutStatus


class DepositRequest(BaseModel):
    amount: Decimal = Field(gt=0, description="Сумма депозита в рублях")


class DepositResponse(BaseModel):
    id: UUID
    brand_id: UUID
    requested_amount: Decimal
    amount: Decimal
    deposit_fee: Decimal
    payout_fee_rate: Decimal
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

class ReleaseRequest(BaseModel):
    payment_id: UUID
    creator_id: UUID
    campaign_id: UUID


class ReleaseResponse(BaseModel):
    payment_id: UUID
    payout_id: UUID
    status: PaymentStatus
    payout_status: PayoutStatus
    fee: Decimal
    payout_amount: Decimal
    platform_fee_payout: Decimal

class WithdrawRequest(BaseModel):
    payout_id: UUID


class WithdrawResponse(BaseModel):
    payout_id: UUID
    status: PayoutStatus
    amount: Decimal

class PlatformFeeResponse(BaseModel):
    value: Decimal
    description: str | None = None
    updated_at: datetime


class PlatformFeeSettingsItem(BaseModel):
    value: Decimal
    description: str | None = None
    updated_at: datetime | None = None


class PlatformFeeSettingsResponse(BaseModel):
    platform_fee: PlatformFeeSettingsItem
    platform_fee_deposit: PlatformFeeSettingsItem
    platform_fee_payout: PlatformFeeSettingsItem

class PlatformFeeUpdate(BaseModel):
    value: Decimal = Field(gt=0, lt=1, description="Размер комиссии платформы (0.0-1.0)")
