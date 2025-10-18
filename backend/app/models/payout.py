"""Creator payout model."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PayoutStatus

if TYPE_CHECKING:  # pragma: no cover
    from app.models.campaign import Campaign
    from app.models.payment import Payment
    from app.models.user import User


class Payout(Base):
    __tablename__ = "payouts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("payments.id", ondelete="SET NULL"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[PayoutStatus] = mapped_column(Enum(PayoutStatus, name="payout_status"), nullable=False, default=PayoutStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())

    creator: Mapped["User"] = relationship("User", back_populates="payouts_received", foreign_keys=[creator_id])
    campaign: Mapped["Campaign"] = relationship("Campaign")
    payment: Mapped["Payment"] = relationship("Payment", back_populates="payouts")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Payout id={self.id} creator_id={self.creator_id} amount={self.amount} status={self.status}>"
