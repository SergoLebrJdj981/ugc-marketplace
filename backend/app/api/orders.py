"""Order endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_db
from app.models import Order, OrderStatus
from app.schemas import OrderListResponse, OrderRead, OrderStatusUpdate

router = APIRouter(prefix="/orders")

SessionDep = Annotated[Session, Depends(get_db)]


@router.get("", response_model=OrderListResponse)
def list_orders(
    *,
    db: SessionDep,
    status_filter: OrderStatus | None = Query(default=None, alias="status"),
    campaign_id: UUID | None = None,
    creator_id: UUID | None = None,
    brand_id: UUID | None = None,
) -> OrderListResponse:
    """Return orders filtered by participant or status."""

    stmt: Select[tuple[Order]] = select(Order)
    if status_filter:
        stmt = stmt.where(Order.status == status_filter)
    if campaign_id:
        stmt = stmt.where(Order.campaign_id == campaign_id)
    if creator_id:
        stmt = stmt.where(Order.creator_id == creator_id)
    if brand_id:
        stmt = stmt.where(Order.brand_id == brand_id)

    items = list(db.scalars(stmt).all())
    return OrderListResponse(items=[OrderRead.model_validate(item) for item in items], total=len(items))


@router.patch("/{order_id}", response_model=OrderRead)
def update_order_status(*, db: SessionDep, order_id: UUID, payload: OrderStatusUpdate) -> OrderRead:
    """Update order status."""

    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order.status = payload.status
    db.add(order)
    db.commit()
    db.refresh(order)
    return OrderRead.model_validate(order)
