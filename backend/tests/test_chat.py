from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Message


def _register_user(client: TestClient, email: str, role: str = "creator") -> dict:
    response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Secret123!",
            "full_name": "Chat Tester",
            "role": role,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_send_and_receive_messages(client: TestClient, db_session: Session) -> None:
    sender_payload = _register_user(client, "chat-sender@example.com", role="brand")
    receiver_payload = _register_user(client, "chat-receiver@example.com", role="creator")

    chat_id = uuid4()
    headers = {"Authorization": f"Bearer {sender_payload['access_token']}"}

    send_response = client.post(
        "/api/chat/send",
        json={
            "chat_id": str(chat_id),
            "receiver_id": receiver_payload["user"]["id"],
            "content": "Привет!",
        },
        headers=headers,
    )
    assert send_response.status_code == 201
    message_data = send_response.json()
    assert message_data["status"] == "success"
    assert message_data["message_id"]
    assert message_data["timestamp"]

    message_in_db = db_session.query(Message).one()
    assert message_in_db.content == "Привет!"
    assert message_in_db.is_read is False

    receiver_headers = {"Authorization": f"Bearer {receiver_payload['access_token']}"}
    history_response = client.get(f"/api/chat/{chat_id}", headers=receiver_headers)
    assert history_response.status_code == 200
    history = history_response.json()
    assert history["total"] == 1
    assert history["items"][0]["content"] == "Привет!"
    assert history["items"][0]["is_read"] is True

    db_session.refresh(message_in_db)
    assert message_in_db.is_read is True

    chat_log = Path(__file__).resolve().parents[2] / "logs" / "chat.log"
    assert chat_log.exists()
    log_contents = chat_log.read_text(encoding="utf-8")
    assert 'status=success' in log_contents
    assert '"Привет!"' in log_contents


def test_websocket_broadcast_on_message(client: TestClient) -> None:
    sender_payload = _register_user(client, "ws-sender@example.com", role="brand")
    receiver_payload = _register_user(client, "ws-receiver@example.com", role="creator")

    chat_id = uuid4()
    ws_token = receiver_payload["access_token"]
    ws_url = f"/ws/chat/{chat_id}?token={ws_token}"

    with client.websocket_connect(ws_url) as websocket:
        send_response = client.post(
            "/api/chat/send",
            json={
                "chat_id": str(chat_id),
                "receiver_id": receiver_payload["user"]["id"],
                "content": "WebSocket message",
            },
            headers={"Authorization": f"Bearer {sender_payload['access_token']}"},
        )
        assert send_response.status_code == 201

        payload = websocket.receive_json()
        assert payload["event"] == "message"
        data = payload["data"]
        assert data["content"] == "WebSocket message"
        assert data["chat_id"] == str(chat_id)
        assert data["receiver_id"] == receiver_payload["user"]["id"]
