"""Operational reports authored by agents or factory teams."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ReportType

if TYPE_CHECKING:  # pragma: no cover
    from app.models.campaign import Campaign
    from app.models.order import Order
    from app.models.user import User


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), index=True)
    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    report_type: Mapped[ReportType] = mapped_column(Enum(ReportType, name="report_type"), nullable=False)
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    author: Mapped[Optional["User"]] = relationship("User", back_populates="authored_reports")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign", back_populates="reports")
    order: Mapped[Optional["Order"]] = relationship("Order")
