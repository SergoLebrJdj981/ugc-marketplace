"""Admin endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/admin")


@router.get("/users")
def list_users():
    return [
        {"id": "demo", "email": "slebronov@mail.ru", "role": "admin"},
    ]


@router.get("/statistics")
def statistics():
    return {
        "data": {
            "total_users": 1,
            "total_campaigns": 1,
            "revenue": "0",
        }
    }
