"""Admin API router."""

from fastapi import APIRouter

from app.api.admin import campaigns, statistics, users

router = APIRouter(prefix="/admin", tags=["Admin"])
router.include_router(users.router, prefix="/users")
router.include_router(campaigns.router, prefix="/campaigns")
router.include_router(statistics.router, prefix="/statistics")
