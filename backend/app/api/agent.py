"""Agent dashboard endpoints."""

from __future__ import annotations

from fastapi import APIRouter, status

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.get("/creators", status_code=status.HTTP_200_OK)
def creators():
    """Return creators supervised by the agent."""

    return {
        "items": [
            {
                "id": "creator-301",
                "name": "Анна Ким",
                "campaigns": 4,
                "avg_rating": 4.9,
                "last_activity": "2025-10-25",
            },
            {
                "id": "creator-302",
                "name": "Дмитрий Орлов",
                "campaigns": 2,
                "avg_rating": 4.6,
                "last_activity": "2025-10-22",
            },
        ]
    }


@router.get("/reports", status_code=status.HTTP_200_OK)
def reports():
    """Return agent reports overview."""

    return {
        "items": [
            {
                "id": "report-71",
                "title": "Месячный отчёт: октябрь",
                "status": "draft",
                "updated_at": "2025-10-25",
            },
            {
                "id": "report-72",
                "title": "Финальный отчёт по Holiday drop",
                "status": "submitted",
                "updated_at": "2025-10-20",
            },
        ]
    }
