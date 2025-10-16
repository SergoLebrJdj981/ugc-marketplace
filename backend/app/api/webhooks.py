"""Webhook endpoints for external integrations."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Order, OrderStatus, Payment, PaymentStatus, WebhookEvent
from app.schemas import (
    OrderWebhookPayload,
    WebhookAckResponse,
    PaymentWebhookPayload,
)
from app.services.notifications import schedule_batch_notifications

logger = logging.getLogger("ugc.webhooks")

router = APIRouter(prefix="/webhooks")

SessionDep = Annotated[Session, Depends(get_db)]


@router.post("/payment", response_model=WebhookAckResponse)
def handle_payment_webhook(
    payload: PaymentWebhookPayload,
    background_tasks: BackgroundTasks,
    db: SessionDep,
) -> WebhookAckResponse:
    """Process payment status updates."""

    payload_dict = payload.model_dump(mode="json")
    logger.info("Received payment webhook: %s", payload_dict)
    event = WebhookEvent(event_type="payment", payload=payload_dict, signature=payload.signature)
    db.add(event)

    payment = db.get(Payment, payload.payment_id)
    if not payment:
        db.commit()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    payment.status = payload.status
    db.add(payment)
    db.commit()

    order = db.get(Order, payment.order_id)
    if order:
        notifications = []
        message = f"Payment {payload.status.value} for order {order.id}"
        notifications.append((order.brand_id, "payment.status", message))
        notifications.append((order.creator_id, "payment.status", message))
        if payload.status == PaymentStatus.COMPLETED:
            notifications.append((order.brand_id, "payment.completed", "Payment completed successfully"))
            notifications.append((order.creator_id, "payment.completed", "Payment completed successfully"))
        schedule_batch_notifications(background_tasks, notifications)

    return WebhookAckResponse(status="accepted")


@router.post("/order", response_model=WebhookAckResponse)
def handle_order_webhook(
    payload: OrderWebhookPayload,
    background_tasks: BackgroundTasks,
    db: SessionDep,
) -> WebhookAckResponse:
    """Process order status updates from external systems."""

    payload_dict = payload.model_dump(mode="json")
    logger.info("Received order webhook: %s", payload_dict)
    event = WebhookEvent(event_type="order", payload=payload_dict, signature=payload.signature)
    db.add(event)

    order = db.get(Order, payload.order_id)
    if not order:
        db.commit()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order.status = payload.status
    db.add(order)
    db.commit()
    db.refresh(order)

    message = payload.message or f"Order {order.id} status updated to {payload.status.value}"
    schedule_batch_notifications(
        background_tasks,
        [
            (order.brand_id, "order.status", message),
            (order.creator_id, "order.status", message),
        ],
    )

    return WebhookAckResponse(status="accepted")
