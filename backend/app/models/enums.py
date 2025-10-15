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
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentType(enum.Enum):
    HOLD = "hold"
    RELEASE = "release"
    PAYOUT = "payout"


class ReportType(enum.Enum):
    AGENT_SUMMARY = "agent_summary"
    FACTORY_STATUS = "factory_status"
    QUALITY_REVIEW = "quality_review"
    ANALYTICS = "analytics"
