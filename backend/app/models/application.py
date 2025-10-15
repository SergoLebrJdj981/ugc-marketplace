"""Application ORM model representing creator proposals."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import ApplicationStatus

if TYPE_CHECKING:  # pragma: no cover
    from app.models.campaign import Campaign
    from app.models.order import Order
    from app.models.user import User


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("campaign_id", "creator_id", name="uq_application_campaign_creator"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus, name="application_status"), nullable=False, default=ApplicationStatus.PENDING)
    pitch: Mapped[str | None] = mapped_column(Text())
    proposed_budget: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    message: Mapped[str | None] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="applications")
    creator: Mapped["User"] = relationship("User", back_populates="applications")
    order: Mapped[Optional["Order"]] = relationship("Order", back_populates="application", uselist=False)
