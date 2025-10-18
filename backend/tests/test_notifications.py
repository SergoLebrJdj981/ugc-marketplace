from __future__ import annotations

from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Notification


def _register_user(client: TestClient, email: str, role: str = "creator") -> dict:
    response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Secret123!",
            "full_name": "Notification Tester",
            "role": role,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_notification_listing(client: TestClient, db_session: Session) -> None:
    user_payload = _register_user(client, "notify@example.com")
    user_id = UUID(user_payload["user"]["id"])

    db_session.add(
        Notification(
            user_id=user_id,
            type="chat_message",
            title="Новое сообщение",
            content="Hello there",
            related_id="chat-1",
        ),
    )
    db_session.commit()

    headers = {"Authorization": f"Bearer {user_payload['access_token']}"}
    response = client.get("/api/notifications", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    item = data["items"][0]
    assert item["title"] == "Новое сообщение"
    assert item["content"] == "Hello there"
    assert item["related_id"] == "chat-1"


def test_mark_notification_read(client: TestClient, db_session: Session) -> None:
    user_payload = _register_user(client, "notify-mark@example.com")
    user_id = UUID(user_payload["user"]["id"])

    note = Notification(
        user_id=user_id,
        type="system",
        title="Тест",
        content="Unread",
    )
    db_session.add(note)
    db_session.commit()

    headers = {"Authorization": f"Bearer {user_payload['access_token']}"}
    response = client.patch(f"/api/notifications/{note.id}/read", headers=headers)
    assert response.status_code == 200
    assert response.json()["updated"] == 1

    db_session.refresh(note)
    assert note.is_read is True


def test_send_notification_requires_admin(client: TestClient) -> None:
    user_payload = _register_user(client, "user@example.com")
    admin_payload = _register_user(client, "admin@example.com", role="admin")

    headers_user = {"Authorization": f"Bearer {user_payload['access_token']}"}
    response = client.post(
        "/api/notifications/send",
        json={
            "user_id": user_payload["user"]["id"],
            "type": "admin_notice",
            "title": "Проверка",
            "content": "Сообщение",
        },
        headers=headers_user,
    )
    assert response.status_code == 403

    headers_admin = {"Authorization": f"Bearer {admin_payload['access_token']}"}
    response = client.post(
        "/api/notifications/send",
        json={
            "user_id": user_payload["user"]["id"],
            "type": "admin_notice",
            "title": "Проверка",
            "content": "Сообщение",
        },
        headers=headers_admin,
    )
    assert response.status_code == 201
    data = response.json()["notification"]
    assert data["title"] == "Проверка"
    assert data["is_read"] is False

    log_path = Path(__file__).resolve().parents[2] / "logs" / "notifications.log"
    assert log_path.exists()
    contents = log_path.read_text(encoding="utf-8")
    assert "title=\"Проверка\"" in contents


def test_notifications_websocket_receives_updates(client: TestClient) -> None:
    user_payload = _register_user(client, "ws-user@example.com")
    admin_payload = _register_user(client, "ws-admin@example.com", role="admin")

    user_id = user_payload["user"]["id"]
    token = user_payload["access_token"]
    ws_url = f"/ws/notifications/{user_id}?token={token}"

    headers_admin = {"Authorization": f"Bearer {admin_payload['access_token']}"}
    with client.websocket_connect(ws_url) as websocket:
        response = client.post(
            "/api/notifications/send",
            json={
                "user_id": user_id,
                "type": "admin_notice",
                "title": "WS",
                "content": "Сообщение",
            },
            headers=headers_admin,
        )
        assert response.status_code == 201
        payload = websocket.receive_json()
        assert payload["event"] == "notification"
        assert payload["data"]["title"] == "WS"
