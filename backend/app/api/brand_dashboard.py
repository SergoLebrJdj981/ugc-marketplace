"""Brand dashboard endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Payment, PaymentStatus, Payout, PayoutStatus, Transaction, TransactionType, User
from app.services.escrow import get_platform_fee, get_platform_fee_deposit, get_platform_fee_payout

router = APIRouter(prefix="/brand", tags=["Brand"])


@router.get("/campaigns", status_code=status.HTTP_200_OK)
def list_campaigns():
    """Return campaigns assigned to the current brand."""

    return {
        "items": [
            {
                "id": "brand-cmp-101",
                "title": "Holiday drop 2025",
                "status": "active",
                "budget": 180000,
                "applications": 24,
            },
            {
                "id": "brand-cmp-102",
                "title": "UGC для retailer launch",
                "status": "draft",
                "budget": 95000,
                "applications": 0,
            },
        ]
    }


@router.post("/campaigns", status_code=status.HTTP_201_CREATED)
def create_campaign(payload: dict):
    """Create a draft campaign (stub implementation)."""

    campaign = {
        "id": "brand-cmp-new",
        "title": payload.get("title", "Новая кампания"),
        "status": "draft",
        "budget": payload.get("budget", 0),
        "created_at": datetime.utcnow().isoformat(),
    }
    return campaign


@router.get("/analytics", status_code=status.HTTP_200_OK)
def analytics():
    """Return analytics metrics for brand dashboards."""

    return {
        "metrics": {
            "ctr": 0.042,
            "cpm": 315,
            "roi": 2.4,
            "reach": 1480000,
        },
        "top_creators": [
            {"id": "creator-1", "name": "Анна Петрова", "orders": 8, "performance": 0.91},
            {"id": "creator-2", "name": "Иван Смирнов", "orders": 5, "performance": 0.87},
        ],
        "recent": [
            {
                "campaign_id": "brand-cmp-101",
                "metric": "views",
                "value": 320000,
                "period": "7d",
            },
            {
                "campaign_id": "brand-cmp-101",
                "metric": "conversions",
                "value": 8200,
                "period": "7d",
            },
        ],
    }


@router.get("/finance", status_code=status.HTTP_200_OK)
def finance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return finance overview for the brand based on escrow data."""

    if current_user.role != "brand":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступно только брендам")

    # Balances
    active_statuses = [PaymentStatus.HOLD, PaymentStatus.RESERVED, PaymentStatus.RELEASED]
    frozen_statuses = [PaymentStatus.HOLD, PaymentStatus.RESERVED]

    balance_total: Decimal = db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0))
        .where(Payment.brand_id == current_user.id)
        .where(Payment.status.in_(active_statuses))
    ).scalar_one()

    frozen_total: Decimal = db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0))
        .where(Payment.brand_id == current_user.id)
        .where(Payment.status.in_(frozen_statuses))
    ).scalar_one()

    expected_total: Decimal = db.execute(
        select(func.coalesce(func.sum(Payout.amount), 0))
        .join(Payment, Payout.payment_id == Payment.id)
        .where(Payment.brand_id == current_user.id)
        .where(Payout.status == PayoutStatus.RELEASED)
    ).scalar_one()

    start_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    spent_this_month: Decimal = db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(Transaction.user_id == current_user.id)
        .where(Transaction.type == TransactionType.RELEASE)
        .where(Transaction.created_at >= start_of_month)
    ).scalar_one()

    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .limit(20)
        .all()
    )

    payment_ids = [txn.reference_id for txn in transactions if txn.reference_type == "payment" and txn.reference_id]
    payments_map: dict[str, Payment] = {}
    if payment_ids:
        payments = db.query(Payment).filter(Payment.id.in_(payment_ids)).all()
        payments_map = {str(payment.id): payment for payment in payments}

    txn_payload = []
    for txn in transactions:
        reference_status = "completed"
        if txn.reference_type == "payment" and txn.reference_id:
            payment = payments_map.get(str(txn.reference_id))
            if payment:
                reference_status = payment.status.value
        txn_payload.append(
            {
                "id": str(txn.id),
                "type": txn.type.value,
                "amount": float(txn.amount),
                "date": txn.created_at.isoformat() if txn.created_at else None,
                "status": reference_status,
                "description": txn.description,
            }
        )

    platform_fee = float(get_platform_fee(db))
    platform_fee_deposit = float(get_platform_fee_deposit(db))
    platform_fee_payout = float(get_platform_fee_payout(db))

    return {
        "balance": float(balance_total),
        "frozen": float(frozen_total),
        "spent_this_month": float(spent_this_month),
        "expected": float(expected_total),
        "platform_fee": platform_fee,
        "platform_fee_deposit": platform_fee_deposit,
        "platform_fee_payout": platform_fee_payout,
        "transactions": txn_payload,
    }
