"""Shared enumerations for ORM models."""

from __future__ import annotations

import enum


class UserRole(enum.Enum):
    BRAND = "brand"
    CREATOR = "creator"
    AGENT = "agent"
    FACTORY = "factory"
    ADMIN = "admin"
    VIEWER = "viewer"


class AdminLevel(enum.Enum):
    NONE = "none"
    ADMIN_LEVEL_1 = "admin_level_1"
    ADMIN_LEVEL_2 = "admin_level_2"
    ADMIN_LEVEL_3 = "admin_level_3"


class CampaignStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ApplicationStatus(enum.Enum):
    PENDING = "pending"
    SHORTLISTED = "shortlisted"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class OrderStatus(enum.Enum):
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    APPROVED = "approved"
    REVISION = "revision"
    CANCELLED = "cancelled"


class VideoStatus(enum.Enum):
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REVISION = "revision"
    REJECTED = "rejected"


class PaymentStatus(enum.Enum):
    HOLD = "hold"
    RESERVED = "reserved"
    RELEASED = "released"
    PAID = "paid"
    REFUNDED = "refunded"


class PayoutStatus(enum.Enum):
    PENDING = "pending"
    RELEASED = "released"
    WITHDRAWN = "withdrawn"


class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    RESERVE = "reserve"
    RELEASE = "release"
    WITHDRAW = "withdraw"
    FEE = "fee"


class ReportType(enum.Enum):
    AGENT_SUMMARY = "agent_summary"
    FACTORY_STATUS = "factory_status"
    QUALITY_REVIEW = "quality_review"
    ANALYTICS = "analytics"


class AdminActionType(enum.Enum):
    BLOCK_USER = "block_user"
    UNBLOCK_USER = "unblock_user"
    BLOCK_CAMPAIGN = "block_campaign"
    UNBLOCK_CAMPAIGN = "unblock_campaign"
    WARNING = "warning"
