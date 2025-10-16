"""Tests for admin API layer."""

from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

from app.models import Campaign, User


def register_and_login(client: TestClient, email: str, *, role: str = "brand", admin_level: str = "none") -> dict:
    register_payload = {
        "email": email,
        "password": "Secret123!",
        "full_name": email.split("@")[0],
        "role": role,
        "admin_level": admin_level,
    }
    res = client.post("/api/auth/register", json=register_payload)
    assert res.status_code == 201
    login = client.post("/api/auth/login", json={"email": email, "password": "Secret123!"})
    assert login.status_code == 200
    return login.json()


def test_admin_access_requires_role(client: TestClient) -> None:
    user_tokens = register_and_login(client, "regular@example.com", admin_level="none")
    response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {user_tokens['access_token']}"},
    )
    assert response.status_code == 403


def test_admin_user_listing_and_role_update(client: TestClient, db_session) -> None:
    admin_tokens = register_and_login(client, "admin1@example.com", admin_level="admin_level_1")
    response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    super_tokens = register_and_login(client, "super@example.com", admin_level="admin_level_3")
    target_tokens = register_and_login(client, "target@example.com", admin_level="none")

    update_resp = client.patch(
        f"/api/admin/users/{target_tokens['user']['id']}/role",
        json={"admin_level": "admin_level_1", "permissions": {"can_review": True}},
        headers={"Authorization": f"Bearer {super_tokens['access_token']}"},
    )
    assert update_resp.status_code == 200
    payload = update_resp.json()
    assert payload["admin_level"] == "admin_level_1"
    assert payload["permissions"]["can_review"] is True


def test_admin_campaign_permissions(client: TestClient, db_session) -> None:
    super_tokens = register_and_login(client, "super2@example.com", admin_level="admin_level_3")
    mod_tokens = register_and_login(client, "mod@example.com", admin_level="admin_level_1")
    brand_tokens = register_and_login(client, "brand_admin@example.com", admin_level="none")

    create_campaign = client.post(
        "/api/campaigns",
        json={
            "title": "Admin Test Campaign",
            "description": "Test",
            "budget": "1000.00",
            "currency": "RUB",
        },
        headers={"Authorization": f"Bearer {brand_tokens['access_token']}"},
    )
    assert create_campaign.status_code == 201
    campaign_id = create_campaign.json()["id"]

    # Moderator can update status
    status_resp = client.patch(
        f"/api/admin/campaigns/{campaign_id}/status",
        json={"status": "paused"},
        headers={"Authorization": f"Bearer {mod_tokens['access_token']}"},
    )
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "paused"

    # Moderator cannot delete
    delete_resp = client.delete(
        f"/api/admin/campaigns/{campaign_id}",
        headers={"Authorization": f"Bearer {mod_tokens['access_token']}"},
    )
    assert delete_resp.status_code == 403

    delete_ok = client.delete(
        f"/api/admin/campaigns/{campaign_id}",
        headers={"Authorization": f"Bearer {super_tokens['access_token']}"},
    )
    assert delete_ok.status_code == 204


def test_admin_statistics_and_export(client: TestClient) -> None:
    finance_tokens = register_and_login(client, "finance@example.com", admin_level="admin_level_2")

    stats_resp = client.get(
        "/api/admin/statistics",
        headers={"Authorization": f"Bearer {finance_tokens['access_token']}"},
    )
    assert stats_resp.status_code == 200
    data = stats_resp.json()["data"]
    assert "totals" in data

    export_resp = client.get(
        "/api/admin/statistics/export",
        headers={"Authorization": f"Bearer {finance_tokens['access_token']}"},
    )
    assert export_resp.status_code == 200
    assert export_resp.headers["content-type"].startswith("text/csv")
