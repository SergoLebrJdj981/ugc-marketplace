"""API router aggregation."""

from fastapi import APIRouter

from app.api import auth, campaigns, notifications, admin, webhooks, system

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router, tags=["Auth"])
api_router.include_router(campaigns.router, tags=["Campaigns"])
api_router.include_router(notifications.router, tags=["Notifications"])   
api_router.include_router(admin.router, tags=["Admin"])
api_router.include_router(webhooks.router, tags=["Webhooks"])
api_router.include_router(system.router, tags=["System"])
