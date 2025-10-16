"""Notifications and webhook behaviour tests."""

from __future__ import annotations

import uuid
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import (
    Application,
    ApplicationStatus,
    Campaign,
    Notification,
    Order,
    OrderStatus,
    Payment,
    PaymentStatus,
    WebhookEvent,
)


def _auth_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    login_response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _register_user(client: TestClient, email: str, role: str) -> uuid.UUID:
    response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Secret123!",
            "full_name": email.split("@")[0].title(),
            "role": role,
        },
    )
    assert response.status_code == 201
    return uuid.UUID(response.json()["id"])


def test_mark_read_notifications(client: TestClient, db_session: Session) -> None:
    user_id = _register_user(client, "notify@example.com", "brand")

    notification = Notification(user_id=user_id, type="test", message="Hello")
    db_session.add(notification)
    db_session.commit()

    resp = client.post(
        "/api/notifications/mark-read",
        json={"notification_ids": [str(notification.id)]},
    )
    assert resp.status_code == 200
    assert resp.json()["updated"] == 1

    db_session.refresh(notification)
    assert notification.is_read is True


def _create_order(
    db_session: Session,
    *,
    campaign_id: uuid.UUID,
    brand_id: uuid.UUID,
    creator_id: uuid.UUID,
) -> Order:
    application = Application(
        campaign_id=campaign_id,
        creator_id=creator_id,
        status=ApplicationStatus.PENDING,
    )
    db_session.add(application)
    db_session.flush()

    order = Order(
        application_id=application.id,
        campaign_id=campaign_id,
        creator_id=creator_id,
        brand_id=brand_id,
        status=OrderStatus.IN_PROGRESS,
        agreed_budget=Decimal("45000.00"),
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


def test_order_status_change_creates_notifications(client: TestClient, db_session: Session) -> None:
    brand_id = _register_user(client, "brand_notify@example.com", "brand")
    creator_id = _register_user(client, "creator_notify@example.com", "creator")
    brand_headers = _auth_headers(client, "brand_notify@example.com", "Secret123!")

    campaign_resp = client.post(
        "/api/campaigns",
        json={
            "title": "Notify campaign",
            "description": "Test campaign",
            "budget": "10000.00",
            "currency": "RUB",
        },
        headers=brand_headers,
    )
    assert campaign_resp.status_code == 201
    campaign_id = uuid.UUID(campaign_resp.json()["id"])

    order = _create_order(db_session, campaign_id=campaign_id, brand_id=brand_id, creator_id=creator_id)

    update_resp = client.patch(
        f"/api/orders/{order.id}",
        json={"status": OrderStatus.APPROVED.value},
    )
    assert update_resp.status_code == 200

    creator_notifications = client.get("/api/notifications", params={"user_id": str(creator_id)})
    assert creator_notifications.status_code == 200
    notifications_payload = creator_notifications.json()
    assert notifications_payload["total"] >= 1
    types = {item["type"] for item in notifications_payload["items"]}
    assert "order.status" in types


def test_payment_webhook_updates_and_notifies(client: TestClient, db_session: Session) -> None:
    brand_id = _register_user(client, "brand_webhook@example.com", "brand")
    creator_id = _register_user(client, "creator_webhook@example.com", "creator")

    campaign = Campaign(
        title="Webhook campaign",
        description="Webhook test",
        budget=Decimal("50000.00"),
        currency="RUB",
        brand_id=brand_id,
    )
    db_session.add(campaign)
    db_session.commit()
    db_session.refresh(campaign)

    order = _create_order(db_session, campaign_id=campaign.id, brand_id=brand_id, creator_id=creator_id)

    payment_resp = client.post(
        "/api/payments",
        json={
            "order_id": str(order.id),
            "payment_type": "hold",
            "amount": "45000.00",
            "currency": "RUB",
        },
    )
    assert payment_resp.status_code == 201
    payment_id = uuid.UUID(payment_resp.json()["id"])

    webhook_resp = client.post(
        "/api/webhooks/payment",
        json={
            "payment_id": str(payment_id),
            "status": PaymentStatus.COMPLETED.value,
            "signature": "test-signature",
        },
    )
    assert webhook_resp.status_code == 200
    assert webhook_resp.json()["status"] == "accepted"

    payment = db_session.get(Payment, payment_id)
    assert payment is not None
    assert payment.status == PaymentStatus.COMPLETED

    events = db_session.query(WebhookEvent).all()
    assert len(events) == 1
    assert events[0].event_type == "payment"

    creator_notifications = client.get("/api/notifications", params={"user_id": str(creator_id)})
    assert creator_notifications.status_code == 200
    types = {item["type"] for item in creator_notifications.json()["items"]}
    assert "payment.completed" in types
