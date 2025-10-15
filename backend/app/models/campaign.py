"""Campaign ORM model."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import CampaignStatus

if TYPE_CHECKING:  # pragma: no cover
    from app.models.application import Application
    from app.models.order import Order
    from app.models.report import Report
    from app.models.user import User


class Campaign(Base):
    __tablename__ = "campaigns"
    __table_args__ = (
        CheckConstraint("budget >= 0", name="campaign_budget_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text())
    brief: Mapped[str | None] = mapped_column(Text())
    budget: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="RUB")
    status: Mapped[CampaignStatus] = mapped_column(Enum(CampaignStatus, name="campaign_status"), nullable=False, default=CampaignStatus.DRAFT)
    start_date: Mapped[date | None] = mapped_column()
    end_date: Mapped[date | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())

    brand: Mapped["User"] = relationship("User", back_populates="campaigns")
    applications: Mapped[list["Application"]] = relationship("Application", back_populates="campaign", cascade="all, delete-orphan")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="campaign", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship("Report", back_populates="campaign")
