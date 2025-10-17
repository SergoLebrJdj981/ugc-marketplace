"""Campaign endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/campaigns")


@router.get("")
def list_campaigns():
    return {
        "items": [
            {"id": "cmp-1", "title": "Demo Campaign", "status": "draft", "budget": 10000},
        ]
    }
