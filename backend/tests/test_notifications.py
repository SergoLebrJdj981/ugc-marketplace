from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Notification, User


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
        Notification(user_id=user_id, type="system", message="Hello there"),
    )
    db_session.commit()

    headers = {"Authorization": f"Bearer {user_payload['access_token']}"}
    response = client.get("/api/notifications", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["message"] == "Hello there"


def test_mark_notifications_read(client: TestClient, db_session: Session) -> None:
    user_payload = _register_user(client, "notify-mark@example.com")
    user_id = UUID(user_payload["user"]["id"])

    note = Notification(user_id=user_id, type="system", message="Unread")
    db_session.add(note)
    db_session.commit()

    headers = {"Authorization": f"Bearer {user_payload['access_token']}"}
    response = client.post(
        "/api/notifications/mark-read",
        json={"notification_ids": [str(note.id)]},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["updated"] == 1

    db_session.refresh(note)
    assert note.is_read is True
