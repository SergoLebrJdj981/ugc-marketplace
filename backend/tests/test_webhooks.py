from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import EventLog


def test_bank_webhook_creates_event(client: TestClient, db_session: Session) -> None:
    response = client.post("/api/webhooks/bank", json={"event": "payment_processed", "amount": 42})
    assert response.status_code == 200
    event = db_session.query(EventLog).order_by(EventLog.id.desc()).first()
    assert event is not None
    assert event.event_type == "bank_webhook"


def test_telegram_webhook_creates_event(client: TestClient, db_session: Session) -> None:
    response = client.post("/api/webhooks/telegram", json={"message": "ping"})
    assert response.status_code == 200
    event = db_session.query(EventLog).order_by(EventLog.id.desc()).first()
    assert event is not None
    assert event.event_type == "telegram_webhook"
