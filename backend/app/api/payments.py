"""Payment endpoints."""

from __future__ import annotations

from typing import Annotated

from sqlalchemy.orm import Session

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.api.deps import get_db
from app.models import Order, Payment, PaymentStatus
from app.schemas import PaymentCreate, PaymentRead
from app.services.notifications import schedule_batch_notifications

router = APIRouter(prefix="/payments")

SessionDep = Annotated[Session, Depends(get_db)]


@router.post("", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(
    *,
    db: SessionDep,
    payload: PaymentCreate,
    background_tasks: BackgroundTasks,
) -> PaymentRead:
    """Create a payment hold for an order."""

    order = db.get(Order, payload.order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    payment = Payment(
        order_id=payload.order_id,
        payment_type=payload.payment_type,
        status=PaymentStatus.PENDING,
        amount=payload.amount,
        currency=payload.currency,
        reference=payload.reference,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)
    message = f"Payment hold created for order {order.id}"
    schedule_batch_notifications(
        background_tasks,
        [
            (order.brand_id, "payment.hold", message),
            (order.creator_id, "payment.hold", message),
        ],
    )
    return PaymentRead.model_validate(payment)
