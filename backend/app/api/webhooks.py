"""Webhook endpoints."""

from fastapi import APIRouter

from app.core.events import event_bus
from app.services.event_logger import log_event

router = APIRouter(prefix="/webhooks")


def _handle(event_type: str, payload: dict):
    log_event(event_type, payload, status="received")
    event_bus.publish(event_type, payload)
    return {"status": "accepted"}


@router.post("/bank")
def bank(payload: dict):
    return _handle("bank_transaction_received", payload)


@router.post("/telegram")
def telegram(payload: dict):
    return _handle("telegram_update", payload)
