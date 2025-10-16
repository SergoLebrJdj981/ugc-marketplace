"""API router aggregation."""

from fastapi import APIRouter

from app.api import auth, campaigns, applications, orders, payments, notifications, webhooks, brands
from app.api.admin import router as admin_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router, tags=["Auth"])
api_router.include_router(campaigns.router, tags=["Campaigns"])
api_router.include_router(brands.router, tags=["Brands"])
api_router.include_router(applications.router, tags=["Applications"])
api_router.include_router(orders.router, tags=["Orders"])
api_router.include_router(payments.router, tags=["Payments"])
api_router.include_router(notifications.router, tags=["Notifications"])
api_router.include_router(webhooks.router, tags=["Webhooks"])
api_router.include_router(admin_router)
