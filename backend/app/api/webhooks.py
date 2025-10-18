"""Webhook endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.events import event_bus
from app.services.event_logger import log_event
from app.services.telegram import handle_telegram_update
from app.api.deps import get_db
from app.schemas import BankWebhookPayload
from app.services.escrow import handle_bank_webhook

router = APIRouter(prefix="/webhooks")


def _handle(event_type: str, payload: dict) -> dict[str, str]:
    log_event(event_type, payload)
    event_bus.publish(event_type, payload)
    return {"status": "accepted"}


@router.post("/bank")
def bank(payload: BankWebhookPayload, db: Session = Depends(get_db)) -> dict[str, object]:
    payload_dict = payload.model_dump()
    base = _handle("bank_webhook", payload_dict)
    result = handle_bank_webhook(db, event=payload.event, payload={k: v for k, v in payload_dict.items() if k != "event"})
    db.commit()
    base.update(result)
    return base


@router.post("/telegram")
async def telegram(payload: dict) -> dict[str, object]:
    base = _handle("telegram_webhook", payload)
    telegram_result = await handle_telegram_update(payload)
    base["telegram"] = telegram_result
    return base
