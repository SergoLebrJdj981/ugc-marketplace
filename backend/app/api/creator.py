"""Creator dashboard endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Payment, Payout, PayoutStatus, Transaction, TransactionType, User
from app.services.escrow import get_platform_fee

router = APIRouter(prefix="/creator", tags=["Creator"])


@router.get("/feed", status_code=status.HTTP_200_OK)
def feed():
    """Return recommended campaigns for the creator feed."""

    now = datetime.utcnow()
    return {
        "items": [
            {
                "id": "cmp-401",
                "title": "Запуск осенней коллекции",
                "brand": "VogueLine",
                "reward": 28000,
                "deadline": (now + timedelta(days=5)).isoformat(),
                "format": "UGC-video",
            },
            {
                "id": "cmp-402",
                "title": "Обзор гаджетов Q4",
                "brand": "TechLab",
                "reward": 32000,
                "deadline": (now + timedelta(days=2)).isoformat(),
                "format": "Shorts",
            },
        ]
    }


@router.get("/orders", status_code=status.HTTP_200_OK)
def orders():
    """Return creator orders grouped by status."""

    return {
        "summary": {
            "in_progress": 3,
            "awaiting_review": 1,
            "completed": 9,
        },
        "items": [
            {
                "id": "order-584",
                "campaign": "Осенний lookbook",
                "status": "in_progress",
                "deadline": "2025-11-02",
                "payout": 26000,
            },
            {
                "id": "order-585",
                "campaign": "Видео-отзыв для TechLab",
                "status": "awaiting_review",
                "deadline": "2025-10-30",
                "payout": 18000,
            },
        ],
    }


@router.get("/balance", status_code=status.HTTP_200_OK)
def balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return financial snapshot for the creator."""

    if current_user.role != "creator":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступно только креаторам")

    available: float = db.execute(
        select(func.coalesce(func.sum(Payout.amount), 0))
        .where(Payout.creator_id == current_user.id)
        .where(Payout.status == PayoutStatus.RELEASED)
    ).scalar_one()

    pending: float = db.execute(
        select(func.coalesce(func.sum(Payout.amount), 0))
        .where(Payout.creator_id == current_user.id)
        .where(Payout.status == PayoutStatus.PENDING)
    ).scalar_one()

    total_earned: float = db.execute(
        select(func.coalesce(func.sum(Payout.amount), 0))
        .where(Payout.creator_id == current_user.id)
    ).scalar_one()

    last_payout = (
        db.query(Payout)
        .filter(Payout.creator_id == current_user.id, Payout.status == PayoutStatus.WITHDRAWN)
        .order_by(Payout.updated_at.desc())
        .first()
    )

    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .limit(20)
        .all()
    )

    txn_payload = [
        {
            "id": str(txn.id),
            "type": txn.type.value,
            "amount": float(txn.amount),
            "date": txn.created_at.isoformat() if txn.created_at else None,
            "status": "completed" if txn.type == TransactionType.WITHDRAW else "processed",
            "description": txn.description,
        }
        for txn in transactions
    ]

    payouts = (
        db.query(Payout)
        .filter(Payout.creator_id == current_user.id)
        .order_by(Payout.created_at.desc())
        .limit(20)
        .all()
    )

    payout_items = [
        {
            "id": str(payout.id),
            "amount": float(payout.amount),
            "status": payout.status.value,
            "created_at": payout.created_at.isoformat() if payout.created_at else None,
            "updated_at": payout.updated_at.isoformat() if payout.updated_at else None,
            "campaign_id": str(payout.campaign_id),
            "payment_id": str(payout.payment_id) if payout.payment_id else None,
        }
        for payout in payouts
    ]

    withdrawable = [item["id"] for item in payout_items if item["status"] == PayoutStatus.RELEASED.value]

    fees_retained: float = db.execute(
        select(func.coalesce(func.sum(Payment.fee), 0))
        .join(Payout, Payment.id == Payout.payment_id)
        .where(Payout.creator_id == current_user.id)
    ).scalar_one()

    platform_fee = float(get_platform_fee(db))

    return {
        "available": float(available),
        "pending": float(pending),
        "total_earned": float(total_earned),
        "last_payout": {
            "amount": float(last_payout.amount) if last_payout else 0.0,
            "date": last_payout.updated_at.isoformat() if last_payout else None,
            "method": "bank_transfer",
        },
        "transactions": txn_payload,
        "payouts": payout_items,
        "withdrawable": withdrawable,
        "retained_fee_total": float(fees_retained),
        "platform_fee": platform_fee,
    }


@router.get("/rating", status_code=status.HTTP_200_OK)
def rating():
    """Return rating metrics for the creator profile."""

    return {
        "score": 4.7,
        "position": 28,
        "total_creators": 520,
        "metrics": {
            "completion_rate": 0.96,
            "avg_review_time": 18,
            "dispute_rate": 0.02,
        },
        "achievements": [
            {"id": "badge-1", "title": "PRO+ автор", "earned_at": "2025-08-12"},
            {"id": "badge-2", "title": "100 кампаний", "earned_at": "2025-09-25"},
        ],
    }


@router.get("/learning", status_code=status.HTTP_200_OK)
def learning():
    """Return learning catalog for the creator."""

    return {
        "tracks": [
            {
                "id": "lrn-105",
                "title": "Advanced TikTok Storytelling",
                "duration": 180,
                "level": "pro",
                "status": "in_progress",
            },
            {
                "id": "lrn-106",
                "title": "Монетизация UGC-контента",
                "duration": 95,
                "level": "pro_plus",
                "status": "available",
            },
        ]
    }
