"""User ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import UserRole

if TYPE_CHECKING:  # pragma: no cover
    from app.models.application import Application
    from app.models.campaign import Campaign
    from app.models.order import Order
    from app.models.rating import Rating
    from app.models.report import Report
    from app.models.notification import Notification


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.CREATOR)
    bio: Mapped[str | None] = mapped_column(String(1000))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    campaigns: Mapped[list["Campaign"]] = relationship("Campaign", back_populates="brand")
    applications: Mapped[list["Application"]] = relationship("Application", back_populates="creator")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="creator", foreign_keys="Order.creator_id")
    authored_reports: Mapped[list["Report"]] = relationship("Report", back_populates="author")
    ratings: Mapped[list["Rating"]] = relationship("Rating", back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
