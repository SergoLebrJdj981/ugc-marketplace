"""API integration tests for core endpoints."""

from __future__ import annotations

import uuid
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Order, OrderStatus


def _auth_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    login_response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login_flow(client: TestClient) -> None:
    register_payload = {
        "email": "brand@example.com",
        "password": "Secret123!",
        "full_name": "Brand Manager",
        "role": "brand",
    }

    register_response = client.post("/api/auth/register", json=register_payload)
    assert register_response.status_code == 201
    user_data = register_response.json()
    assert user_data["email"] == register_payload["email"]
    assert "id" in user_data

    login_response = client.post(
        "/api/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert token_data["token_type"] == "bearer"
    assert token_data["user"]["email"] == register_payload["email"]
    assert "refresh_token" in token_data


def test_refresh_and_logout_flow(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={
            "email": "refresher@example.com",
            "password": "Secret123!",
            "full_name": "Refresher",
            "role": "brand",
        },
    )

    login_response = client.post(
        "/api/auth/login",
        json={"email": "refresher@example.com", "password": "Secret123!"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()

    refresh_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    refreshed = refresh_response.json()
    assert refreshed["access_token"] != tokens["access_token"]
    assert refreshed["refresh_token"] != tokens["refresh_token"]

    logout_response = client.post(
        "/api/auth/logout",
        json={"refresh_token": refreshed["refresh_token"]},
    )
    assert logout_response.status_code == 204

    invalid_refresh = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refreshed["refresh_token"]},
    )
    assert invalid_refresh.status_code == 401

def test_campaign_creation_and_listing(client: TestClient) -> None:
    brand_resp = client.post(
        "/api/auth/register",
        json={
            "email": "brand2@example.com",
            "password": "Secret123!",
            "full_name": "Brand Two",
            "role": "brand",
        },
    )
    assert brand_resp.status_code == 201
    headers = _auth_headers(client, "brand2@example.com", "Secret123!")

    create_resp = client.post(
        "/api/campaigns",
        json={
            "title": "Winter Promo",
            "description": "UGC drive for New Year",
            "budget": "200000.00",
            "currency": "RUB",
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    campaign_data = create_resp.json()
    assert campaign_data["title"] == "Winter Promo"
    assert campaign_data["status"] == "draft"

    list_resp = client.get("/api/campaigns", params={"status": "draft"})
    assert list_resp.status_code == 200
    campaigns = list_resp.json()
    assert campaigns["total"] == 1
    assert campaigns["items"][0]["id"] == campaign_data["id"]


def test_payment_flow(client: TestClient, db_session: Session) -> None:
    brand_resp = client.post(
        "/api/auth/register",
        json={
            "email": "brand3@example.com",
            "password": "Secret123!",
            "full_name": "Brand Three",
            "role": "brand",
        },
    )
    brand_id = uuid.UUID(brand_resp.json()["id"])
    brand_headers = _auth_headers(client, "brand3@example.com", "Secret123!")

    creator_resp = client.post(
        "/api/auth/register",
        json={
            "email": "creator@example.com",
            "password": "Secret123!",
            "full_name": "Creator One",
            "role": "creator",
        },
    )
    creator_id = uuid.UUID(creator_resp.json()["id"])

    campaign_resp = client.post(
        "/api/campaigns",
        json={
            "title": "Spring Launch",
            "description": "Launch campaign",
            "budget": "100000.00",
            "currency": "RUB",
        },
        headers=brand_headers,
    )
    campaign_id = uuid.UUID(campaign_resp.json()["id"])

    application_resp = client.post(
        "/api/applications",
        json={
            "campaign_id": str(campaign_id),
            "creator_id": str(creator_id),
            "pitch": "I can deliver great content",
            "proposed_budget": "45000.00",
        },
    )
    application_id = uuid.UUID(application_resp.json()["id"])

    order = Order(
        application_id=application_id,
        campaign_id=campaign_id,
        creator_id=creator_id,
        brand_id=brand_id,
        status=OrderStatus.IN_PROGRESS,
        agreed_budget=Decimal("45000.00"),
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

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
    payment_data = payment_resp.json()
    assert payment_data["order_id"] == str(order.id)
    assert payment_data["status"] == "pending"
    assert payment_data["amount"] == "45000.00"
