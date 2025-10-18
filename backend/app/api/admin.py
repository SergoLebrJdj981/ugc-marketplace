"""Admin endpoints."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_db, require_admin
from app.db.session import get_session
from app.models import (
    AdminLevel,
    Campaign,
    EventLog,
    Notification,
    Payment,
    PaymentStatus,
    Payout,
    PayoutStatus,
    SystemSetting,
    Transaction,
    User,
)
from app.schemas import (
    PlatformFeeResponse,
    PlatformFeeSettingsItem,
    PlatformFeeSettingsResponse,
    PlatformFeeUpdate,
)
from app.services.escrow import (
    get_platform_fee,
    get_platform_fee_deposit,
    get_platform_fee_payout,
    set_platform_fee,
    set_platform_fee_deposit,
    set_platform_fee_payout,
)

router = APIRouter(prefix="/admin")


@router.get("/users")
def list_users(db: Session = Depends(get_session)):
    users = db.query(User).all()
    return [
        {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        }
        for user in users
    ]


@router.get("/statistics")
def statistics(db: Session = Depends(get_session)):
    user_count = db.query(func.count(User.id)).scalar() or 0
    notification_count = db.query(func.count(Notification.id)).scalar() or 0
    event_count = db.query(func.count(EventLog.id)).scalar() or 0
    return {
        "total_users": int(user_count),
        "total_notifications": int(notification_count),
        "total_events": int(event_count),
    }


@router.get("/campaigns")
def campaigns(db: Session = Depends(get_session)):
    """Return campaign overview for admin dashboard."""

    campaigns = db.query(Campaign).all()
    if not campaigns:
        return {
            "items": [
                {
                    "id": "cmp-virtual-1",
                    "title": "Demo Campaign",
                    "brand": "Demo Brand",
                    "status": "draft",
                    "budget": 50000,
                    "created_at": datetime.utcnow().isoformat(),
                }
            ]
        }
    return {
        "items": [
            {
                "id": str(campaign.id),
                "title": campaign.title,
                "brand": campaign.brand.name if campaign.brand else "—",
                "status": campaign.status.value if hasattr(campaign.status, "value") else getattr(campaign, "status"),
                "budget": float(getattr(campaign, "budget", 0) or 0),
                "created_at": getattr(campaign, "created_at", datetime.utcnow()).isoformat(),
            }
            for campaign in campaigns
        ]
    }


@router.get("/finance")
def finance_overview(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin(AdminLevel.ADMIN_LEVEL_2)),
):
    """Return finance metrics for admin dashboard."""

    escrow_balance = db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status.in_([PaymentStatus.HOLD, PaymentStatus.RESERVED, PaymentStatus.RELEASED])
        )
    ).scalar_one()

    total_payouts = db.execute(
        select(func.coalesce(func.sum(Payout.amount), 0)).where(Payout.status == PayoutStatus.WITHDRAWN)
    ).scalar_one()

    processing = db.execute(
        select(func.coalesce(func.sum(Payout.amount), 0)).where(Payout.status == PayoutStatus.RELEASED)
    ).scalar_one()

    recent_transactions = (
        db.query(Transaction)
        .order_by(Transaction.created_at.desc())
        .limit(20)
        .all()
    )

    recent_payload = [
        {
            "id": str(txn.id),
            "type": txn.type.value,
            "amount": float(txn.amount),
            "status": txn.type.value,
            "date": txn.created_at.isoformat() if txn.created_at else None,
        }
        for txn in recent_transactions
    ]

    fees_collected = db.execute(
        select(func.coalesce(func.sum(Payment.fee), 0))
    ).scalar_one()

    platform_fee = float(get_platform_fee(db))
    platform_fee_deposit = float(get_platform_fee_deposit(db))
    platform_fee_payout = float(get_platform_fee_payout(db))
    db.commit()

    return {
        "metrics": {
            "total_payouts": float(total_payouts),
            "escrow_balance": float(escrow_balance),
            "processing": float(processing),
            "fees_collected": float(fees_collected),
            "platform_fee": platform_fee,
            "platform_fee_deposit": platform_fee_deposit,
            "platform_fee_payout": platform_fee_payout,
        },
        "recent": recent_payload,
    }


@router.get("/analytics")
def analytics_overview(db: Session = Depends(get_session)):
    """Return admin-level analytics data."""

    totals = db.query(func.count(EventLog.id)).scalar() or 0
    return {
        "total_events": int(totals),
        "per_status": {
            status: count
            for status, count in db.query(EventLog.status, func.count(EventLog.id)).group_by(EventLog.status)
        },
        "systems": {
            "auth": {"incidents": 0, "uptime": 0.999},
            "api": {"incidents": 1, "uptime": 0.995},
            "notifications": {"incidents": 0, "uptime": 0.998},
        },
    }
@router.get("/settings", response_model=PlatformFeeSettingsResponse)
def list_platform_fee_settings(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin(AdminLevel.ADMIN_LEVEL_2)),
) -> PlatformFeeSettingsResponse:
    base_value = get_platform_fee(db)
    deposit_value = get_platform_fee_deposit(db)
    payout_value = get_platform_fee_payout(db)

    base_setting = db.query(SystemSetting).filter(SystemSetting.key == "platform_fee").one()
    deposit_setting = db.query(SystemSetting).filter(SystemSetting.key == "platform_fee_deposit").one()
    payout_setting = db.query(SystemSetting).filter(SystemSetting.key == "platform_fee_payout").one()
    db.commit()
    for setting in (base_setting, deposit_setting, payout_setting):
        db.refresh(setting)

    return PlatformFeeSettingsResponse(
        platform_fee=_settings_item(base_setting, base_value),
        platform_fee_deposit=_settings_item(deposit_setting, deposit_value),
        platform_fee_payout=_settings_item(payout_setting, payout_value),
    )


@router.get("/settings/platform_fee", response_model=PlatformFeeResponse)
def platform_fee_settings(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin(AdminLevel.ADMIN_LEVEL_2)),
) -> PlatformFeeResponse:
    value = get_platform_fee(db)
    setting = db.query(SystemSetting).filter(SystemSetting.key == "platform_fee").one_or_none()
    if setting is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Настройка комиссии не найдена")
    db.commit()
    db.refresh(setting)
    return _settings_response(setting, value)


@router.patch("/settings/platform_fee", response_model=PlatformFeeResponse)
def update_platform_fee_setting(
    payload: PlatformFeeUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin(AdminLevel.ADMIN_LEVEL_3)),
) -> PlatformFeeResponse:
    setting = set_platform_fee(db, payload.value, actor=admin)
    db.commit()
    db.refresh(setting)
    return _settings_response(setting, Decimal(setting.value))


@router.get("/settings/platform_fee_deposit", response_model=PlatformFeeResponse)
def platform_fee_deposit_settings(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin(AdminLevel.ADMIN_LEVEL_2)),
) -> PlatformFeeResponse:
    value = get_platform_fee_deposit(db)
    setting = db.query(SystemSetting).filter(SystemSetting.key == "platform_fee_deposit").one_or_none()
    if setting is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Настройка комиссии не найдена")
    db.commit()
    db.refresh(setting)
    return _settings_response(setting, value)


@router.patch("/settings/platform_fee_deposit", response_model=PlatformFeeResponse)
def update_platform_fee_deposit_setting(
    payload: PlatformFeeUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin(AdminLevel.ADMIN_LEVEL_3)),
) -> PlatformFeeResponse:
    setting = set_platform_fee_deposit(db, payload.value, actor=admin)
    db.commit()
    db.refresh(setting)
    return _settings_response(setting, Decimal(setting.value))


@router.get("/settings/platform_fee_payout", response_model=PlatformFeeResponse)
def platform_fee_payout_settings(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin(AdminLevel.ADMIN_LEVEL_2)),
) -> PlatformFeeResponse:
    value = get_platform_fee_payout(db)
    setting = db.query(SystemSetting).filter(SystemSetting.key == "platform_fee_payout").one_or_none()
    if setting is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Настройка комиссии не найдена")
    db.commit()
    db.refresh(setting)
    return _settings_response(setting, value)


@router.patch("/settings/platform_fee_payout", response_model=PlatformFeeResponse)
def update_platform_fee_payout_setting(
    payload: PlatformFeeUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin(AdminLevel.ADMIN_LEVEL_3)),
) -> PlatformFeeResponse:
    setting = set_platform_fee_payout(db, payload.value, actor=admin)
    db.commit()
    db.refresh(setting)
    return _settings_response(setting, Decimal(setting.value))


def _settings_item(setting: SystemSetting, value: Decimal) -> PlatformFeeSettingsItem:
    return PlatformFeeSettingsItem(
        value=value,
        description=setting.description,
        updated_at=setting.updated_at,
    )


def _settings_response(setting: SystemSetting, value: Decimal) -> PlatformFeeResponse:
    return PlatformFeeResponse(value=value, description=setting.description, updated_at=setting.updated_at)
