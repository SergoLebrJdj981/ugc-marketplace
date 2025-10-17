"""Brand dashboard endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, status

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
def finance():
    """Return finance overview for the brand."""

    return {
        "balance": 245000,
        "frozen": 78000,
        "spent_this_month": 96000,
        "expected": 54000,
        "transactions": [
            {
                "id": "txn-201",
                "type": "payout",
                "amount": 42000,
                "date": "2025-10-21",
                "status": "completed",
            },
            {
                "id": "txn-202",
                "type": "escrow",
                "amount": 36000,
                "date": "2025-10-24",
                "status": "processing",
            },
        ],
    }
