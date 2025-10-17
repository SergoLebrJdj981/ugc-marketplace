"""Creator dashboard endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, status

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
def balance():
    """Return financial snapshot for the creator."""

    return {
        "available": 74500,
        "pending": 21000,
        "total_earned": 412000,
        "last_payout": {
            "amount": 38000,
            "date": "2025-10-18",
            "method": "bank_transfer",
        },
        "transactions": [
            {
                "id": "txn-901",
                "type": "payout",
                "amount": 38000,
                "date": "2025-10-18",
                "status": "completed",
            },
            {
                "id": "txn-902",
                "type": "escrow",
                "amount": 21000,
                "date": "2025-10-22",
                "status": "pending",
            },
        ],
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
