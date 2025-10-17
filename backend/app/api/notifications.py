"""Notification endpoints."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/notifications")


@router.get("")
def list_notifications(user_id: str | None = None):
    return {
        "items": [
            {
                "id": "notif-1",
                "user_id": user_id or "demo-user-id",
                "type": "system",
                "message": "Welcome to UGC Marketplace",
                "is_read": False,
            }
        ]
    }


@router.post("/mark-read")
def mark_read(payload: dict[str, list[str]]):
    return {"updated": len(payload.get("notification_ids", []))}
