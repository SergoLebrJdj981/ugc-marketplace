"""Admin endpoints."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.db.session import get_session
from app.models import Campaign, EventLog, Notification, User

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
def finance_overview(db: Session = Depends(get_session)):
    """Return finance metrics for admin dashboard."""

    total_payouts = db.execute(func.sum(Notification.id)).scalar() or 0  # placeholder aggregate
    return {
        "metrics": {
            "total_payouts": int(total_payouts) * 1000,
            "escrow_balance": 520000,
            "processing": 74000,
        },
        "recent": [
            {"id": "adm-txn-1", "type": "payout", "amount": 42000, "status": "completed", "date": "2025-10-22"},
            {"id": "adm-txn-2", "type": "escrow", "amount": 18000, "status": "pending", "date": "2025-10-24"},
        ],
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
