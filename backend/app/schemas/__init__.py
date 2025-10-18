"""Aggregate Pydantic schemas for external imports."""

from app.schemas.admin import (
    AdminCampaignStatusUpdate,
    AdminExportResponse,
    AdminUserRoleUpdate,
    StatisticsResponse,
)
from app.schemas.application import ApplicationCreate, ApplicationRead
from app.schemas.brand import BrandCreate, BrandRead
from app.schemas.campaign import CampaignCreate, CampaignListResponse, CampaignRead
from app.schemas.notification import (
    NotificationListResponse,
    NotificationMarkReadRequest,
    NotificationMarkReadResponse,
    NotificationRead,
)
from app.schemas.chat import MessageListResponse, MessageRead, MessageSendRequest, MessageSendResponse
from app.schemas.order import OrderListResponse, OrderRead, OrderStatusUpdate
from app.schemas.payment import PaymentCreate, PaymentRead
from app.schemas.webhook import (
    OrderWebhookPayload,
    PaymentWebhookPayload,
    WebhookAckResponse,
    WebhookEventRead,
)
from app.schemas.user import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse

__all__ = [
    "AdminCampaignStatusUpdate",
    "AdminExportResponse",
    "AdminUserRoleUpdate",
    "StatisticsResponse",
    "ApplicationCreate",
    "ApplicationRead",
    "BrandCreate",
    "BrandRead",
    "CampaignCreate",
    "CampaignListResponse",
    "CampaignRead",
    "LoginRequest",
    "MessageListResponse",
    "MessageRead",
    "MessageSendRequest",
    "MessageSendResponse",
    "NotificationListResponse",
    "NotificationMarkReadRequest",
    "NotificationMarkReadResponse",
    "NotificationRead",
    "OrderListResponse",
    "OrderRead",
    "OrderStatusUpdate",
    "PaymentCreate",
    "PaymentRead",
    "OrderWebhookPayload",
    "PaymentWebhookPayload",
    "WebhookAckResponse",
    "WebhookEventRead",
    "TokenResponse",
    "RefreshRequest",
    "RegisterRequest",
]
