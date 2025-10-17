"""Factory (content team) dashboard endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, status

router = APIRouter(prefix="/factory", tags=["Factory"])


@router.get("/tasks", status_code=status.HTTP_200_OK)
def tasks():
    """Return production tasks assigned to the factory team."""

    now = datetime.utcnow()
    return {
        "items": [
            {
                "id": "task-501",
                "title": "Монтаж ролика для Holiday drop",
                "status": "in_progress",
                "due_date": (now + timedelta(days=1)).isoformat(),
            },
            {
                "id": "task-502",
                "title": "Пост-продакшн TikTok live",
                "status": "scheduled",
                "due_date": (now + timedelta(days=3)).isoformat(),
            },
        ]
    }


@router.get("/calendar", status_code=status.HTTP_200_OK)
def calendar():
    """Return production calendar entries."""

    today = datetime.utcnow().date()
    return {
        "items": [
            {
                "id": "cal-301",
                "title": "Публикация ролика в Instagram",
                "date": today.isoformat(),
                "campaign": "Holiday drop 2025",
            },
            {
                "id": "cal-302",
                "title": "Съёмка для TechLab",
                "date": (today + timedelta(days=2)).isoformat(),
                "campaign": "TechLab gadgets",
            },
        ]
    }
