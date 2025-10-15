"""Video submission model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import VideoStatus

if TYPE_CHECKING:  # pragma: no cover
    from app.models.order import Order


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    storage_url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[VideoStatus] = mapped_column(Enum(VideoStatus, name="video_status"), nullable=False, default=VideoStatus.SUBMITTED)
    notes: Mapped[str | None] = mapped_column(Text())
    submitted_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column()

    order: Mapped["Order"] = relationship("Order", back_populates="videos")
