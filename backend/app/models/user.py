"""User model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:  # pragma: no cover
    from app.models.application import Application
    from app.models.campaign import Campaign
    from app.models.notification import Notification
    from app.models.order import Order
    from app.models.report import Report

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="creator")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1", nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    applications: Mapped[list["Application"]] = relationship(
        "Application",
        back_populates="creator",
        cascade="all, delete-orphan",
        foreign_keys="Application.creator_id",
    )
    campaigns: Mapped[list["Campaign"]] = relationship(
        "Campaign",
        back_populates="brand",
        cascade="all, delete-orphan",
        foreign_keys="Campaign.brand_id",
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="creator",
        cascade="all, delete-orphan",
        foreign_keys="Order.creator_id",
    )
    orders_as_brand: Mapped[list["Order"]] = relationship(
        "Order",
        cascade="all, delete-orphan",
        foreign_keys="Order.brand_id",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        backref="user",
        cascade="all, delete-orphan",
    )
    authored_reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="author",
        cascade="all, delete-orphan",
        foreign_keys="Report.author_id",
    )
