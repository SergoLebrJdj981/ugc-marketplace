"""Webhook endpoints."""

from fastapi import APIRouter

from app.core.events import event_bus
from app.services.event_logger import log_event
from app.services.telegram import handle_telegram_update

router = APIRouter(prefix="/webhooks")


def _handle(event_type: str, payload: dict) -> dict[str, str]:
    log_event(event_type, payload)
    event_bus.publish(event_type, payload)
    return {"status": "accepted"}


@router.post("/bank")
def bank(payload: dict) -> dict[str, str]:
    return _handle("bank_webhook", payload)


@router.post("/telegram")
async def telegram(payload: dict) -> dict[str, object]:
    base = _handle("telegram_webhook", payload)
    telegram_result = await handle_telegram_update(payload)
    base["telegram"] = telegram_result
    return base
