"""API router aggregation."""

from fastapi import APIRouter

from app.api import (
    admin,
    admin_moderation,
    agent,
    auth,
    chat,
    brand_dashboard,
    campaigns,
    creator,
    factory,
    notifications,
    payments,
    payouts,
    system,
    webhooks,
)

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router, tags=["Auth"])
api_router.include_router(campaigns.router, tags=["Campaigns"])
api_router.include_router(chat.router)
api_router.include_router(creator.router)
api_router.include_router(brand_dashboard.router)
api_router.include_router(agent.router)
api_router.include_router(factory.router)
api_router.include_router(notifications.router, tags=["Notifications"])
api_router.include_router(payments.router, tags=["Payments"])
api_router.include_router(payouts.router, tags=["Payouts"])
api_router.include_router(admin.router, tags=["Admin"])
api_router.include_router(admin_moderation.router, tags=["Admin Moderation"])
api_router.include_router(webhooks.router, tags=["Webhooks"])
api_router.include_router(system.router, tags=["System"])
