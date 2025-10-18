from __future__ import annotations

from pathlib import Path
from uuid import UUID
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.main import app
from app.models import TelegramLink


def test_telegram_webhook_handles_commands(monkeypatch):
    client = TestClient(app)

    async_mock = AsyncMock(return_value="delivered")
    monkeypatch.setattr("app.services.telegram.send_telegram_message", async_mock)

    payload = {
        "message": {
            "chat": {"id": 12345},
            "text": "/start",
        }
    }

    response = client.post("/api/webhooks/telegram", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["telegram"]["status"] == "delivered"
    async_mock.assert_awaited()

    log_path = Path(__file__).resolve().parents[2] / "logs" / "telegram.log"
    assert log_path.exists()
    assert "status=delivered" in log_path.read_text(encoding="utf-8")


def test_telegram_webhook_ignores_missing_text(monkeypatch):
    client = TestClient(app)

    async_mock = AsyncMock(return_value="delivered")
    monkeypatch.setattr("app.services.telegram.send_telegram_message", async_mock)

    payload = {"message": {"chat": {"id": 54321}}}
    response = client.post("/api/webhooks/telegram", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["telegram"]["status"] == "ignored"
    async_mock.assert_not_awaited()


def test_telegram_start_links_user(monkeypatch, client: TestClient) -> None:
    user_payload = client.post(
        "/api/auth/register",
        json={
            "email": "tg-link@example.com",
            "password": "Secret123!",
            "full_name": "Telegram Link",
            "role": "creator",
        },
    ).json()

    async_mock = AsyncMock(return_value="delivered")
    monkeypatch.setattr("app.services.telegram.send_telegram_message", async_mock)

    user_id = user_payload["user"]["id"]
    payload = {
        "message": {
            "chat": {"id": 987654321},
            "text": f"/start {user_id}",
            "from": {"id": 987654321, "username": "tester", "first_name": "Test"},
        }
    }

    response = client.post("/api/webhooks/telegram", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["telegram"]["status"] == "delivered"

    from app.services import telegram as telegram_service

    with telegram_service.SessionLocal() as session:
        link = (
            session.query(TelegramLink)
            .filter(TelegramLink.user_id == UUID(user_id), TelegramLink.telegram_id == 987654321)
            .one_or_none()
        )
        assert link is not None
        assert link.is_active is True
    async_mock.assert_awaited()
