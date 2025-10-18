"""Escrow payment model."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PaymentStatus

if TYPE_CHECKING:  # pragma: no cover
    from app.models.transaction import Transaction
    from app.models.user import User
    from app.models.payout import Payout


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    deposit_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus, name="payment_status"), nullable=False, default=PaymentStatus.HOLD)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())

    brand: Mapped["User"] = relationship("User", back_populates="payments_made", foreign_keys=[brand_id])
    payouts: Mapped[list["Payout"]] = relationship("Payout", back_populates="payment", cascade="all, delete-orphan")
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        primaryjoin="Payment.id == foreign(Transaction.reference_id)",
        viewonly=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"<Payment id={self.id} brand_id={self.brand_id} amount={self.amount} "
            f"deposit_fee={self.deposit_fee} status={self.status}>"
        )
