"""API router aggregation."""

from fastapi import APIRouter

from app.api import auth, campaigns, applications, orders, payments, notifications

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router, tags=["Auth"])
api_router.include_router(campaigns.router, tags=["Campaigns"])
api_router.include_router(applications.router, tags=["Applications"])
api_router.include_router(orders.router, tags=["Orders"])
api_router.include_router(payments.router, tags=["Payments"])
api_router.include_router(notifications.router, tags=["Notifications"])
