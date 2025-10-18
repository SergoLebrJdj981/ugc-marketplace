from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app


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
