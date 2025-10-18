"""Order ORM model representing approved collaborations."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import OrderStatus

if TYPE_CHECKING:  # pragma: no cover
    from app.models.application import Application
    from app.models.campaign import Campaign
    from app.models.user import User
    from app.models.video import Video


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("application_id", name="uq_order_application"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    brand_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus, name="order_status"), nullable=False, default=OrderStatus.IN_PROGRESS)
    agreed_budget: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    deliverables: Mapped[str | None] = mapped_column(Text())
    delivery_due: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    application: Mapped["Application"] = relationship("Application", back_populates="order")
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="orders")
    creator: Mapped["User"] = relationship("User", back_populates="orders", foreign_keys=[creator_id])
    brand: Mapped["User"] = relationship("User", back_populates="orders_as_brand", foreign_keys=[brand_id])
    videos: Mapped[list["Video"]] = relationship("Video", back_populates="order", cascade="all, delete-orphan")
