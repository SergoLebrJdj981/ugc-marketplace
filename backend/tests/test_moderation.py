from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.core.config import PROJECT_ROOT
from app.core.security import create_access_token, hash_password
from app.models import (
    AdminAction,
    AdminActionType,
    AdminLevel,
    Campaign,
    CampaignStatus,
    Notification,
    User,
)


@pytest.fixture
def admin_user(db_session) -> User:
    admin = User(
        email="moderator@example.com",
        password=hash_password("Secret123!"),
        role="admin",
        full_name="Moderator",
        admin_level=AdminLevel.ADMIN_LEVEL_3,
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def admin_token(admin_user: User) -> str:
    return create_access_token({"sub": str(admin_user.id), "role": admin_user.role})


@pytest.fixture
def target_user(db_session) -> User:
    user = User(
        email="creator@example.com",
        password=hash_password("Secret123!"),
        role="creator",
        full_name="Creator User",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def brand_user(db_session) -> User:
    user = User(
        email="brand@example.com",
        password=hash_password("Secret123!"),
        role="brand",
        full_name="Brand Owner",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_campaign(db_session, brand_user: User) -> Campaign:
    campaign = Campaign(
        brand_id=brand_user.id,
        title="Test Campaign",
        description="Demo description",
        budget=Decimal("1000.00"),
        currency="RUB",
        status=CampaignStatus.ACTIVE,
    )
    db_session.add(campaign)
    db_session.commit()
    db_session.refresh(campaign)
    return campaign


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_user_block_and_unblock_flow(
    client: TestClient,
    db_session,
    admin_token: str,
    target_user: User,
) -> None:
    response = client.patch(
        f"/api/admin/moderation/user/{target_user.id}/block",
        json={"blocked": True, "reason": "Подозрительная активность"},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["status"] == "blocked"
    db_session.refresh(target_user)
    assert target_user.is_active is False

    # A notification should be created for the user
    notif_count = db_session.query(Notification).filter(Notification.user_id == target_user.id).count()
    assert notif_count == 1

    log_path = PROJECT_ROOT / "logs" / "actions.log"
    assert "action=block_user" in log_path.read_text(encoding="utf-8")

    unblock_response = client.patch(
        f"/api/admin/moderation/user/{target_user.id}/block",
        json={"blocked": False, "reason": "Ошибочная блокировка"},
        headers=auth_headers(admin_token),
    )
    assert unblock_response.status_code == 200
    db_session.refresh(target_user)
    assert target_user.is_active is True

    db_session.expire_all()
    actions = (
        db_session.query(AdminAction)
        .filter(AdminAction.target_id == target_user.id)
        .order_by(AdminAction.created_at.asc())
        .all()
    )
    assert len(actions) == 2
    assert {action.action_type for action in actions} == {
        AdminActionType.BLOCK_USER,
        AdminActionType.UNBLOCK_USER,
    }

    notif_total = db_session.query(Notification).filter(Notification.user_id == target_user.id).count()
    assert notif_total == 2


def test_campaign_block_flow(
    client: TestClient,
    db_session,
    admin_token: str,
    test_campaign: Campaign,
) -> None:
    response = client.patch(
        f"/api/admin/moderation/campaign/{test_campaign.id}/block",
        json={"blocked": True, "reason": "Запрещённый контент"},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    db_session.refresh(test_campaign)
    assert test_campaign.is_blocked is True

    action = (
        db_session.query(AdminAction)
        .filter(AdminAction.target_id == test_campaign.id)
        .one()
    )
    assert action.action_type == AdminActionType.BLOCK_CAMPAIGN

    owner_notifications = (
        db_session.query(Notification)
        .filter(Notification.user_id == test_campaign.brand_id)
        .count()
    )
    assert owner_notifications == 1


def test_warning_creates_notification_and_log(
    client: TestClient,
    db_session,
    admin_token: str,
    target_user: User,
) -> None:
    payload = {"user_id": str(target_user.id), "message": "Публикация не соответствует правилам"}
    response = client.post(
        "/api/admin/moderation/warning",
        json=payload,
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 201

    action = (
        db_session.query(AdminAction)
        .filter(AdminAction.target_id == target_user.id)
        .one()
    )
    assert action.action_type == AdminActionType.WARNING

    notification = (
        db_session.query(Notification)
        .filter(Notification.user_id == target_user.id)
        .one()
    )
    assert "предупреждение" in notification.title.lower()

    log_path = PROJECT_ROOT / "logs" / "actions.log"
    text = log_path.read_text(encoding="utf-8")
    assert "ADMIN WARNING" in text
    assert "Публикация не соответствует правилам" in text


def test_logs_and_listing_endpoints(
    client: TestClient,
    db_session,
    admin_token: str,
    target_user: User,
    test_campaign: Campaign,
) -> None:
    # Generate some actions
    client.patch(
        f"/api/admin/moderation/user/{target_user.id}/block",
        json={"blocked": True},
        headers=auth_headers(admin_token),
    )
    client.patch(
        f"/api/admin/moderation/campaign/{test_campaign.id}/block",
        json={"blocked": True},
        headers=auth_headers(admin_token),
    )

    users_response = client.get(
        "/api/admin/moderation/users",
        headers=auth_headers(admin_token),
    )
    assert users_response.status_code == 200
    users_payload = users_response.json()
    assert users_payload["total"] >= 1
    assert any(item["id"] == str(target_user.id) for item in users_payload["items"])

    campaigns_response = client.get(
        "/api/admin/moderation/campaigns",
        headers=auth_headers(admin_token),
    )
    assert campaigns_response.status_code == 200
    campaigns_payload = campaigns_response.json()
    assert campaigns_payload["total"] >= 1
    assert any(item["id"] == str(test_campaign.id) for item in campaigns_payload["items"])

    logs_response = client.get(
        "/api/admin/moderation/logs",
        headers=auth_headers(admin_token),
    )
    assert logs_response.status_code == 200
    logs_payload = logs_response.json()
    assert logs_payload["total"] >= 2
    assert all("action_type" in item for item in logs_payload["items"])
