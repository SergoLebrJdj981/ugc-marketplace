"""Moderation workflow helpers for admin panel."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import PROJECT_ROOT
from app.models import AdminAction, AdminActionType, Campaign, User
from app.services.notifications import create_notification

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "actions.log"
LOG_FILE.touch(exist_ok=True)


def _format_timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def _append_log(
    *,
    kind: Literal["ACTION", "WARNING"],
    admin_id: UUID,
    target_label: Literal["user", "campaign"],
    target_id: UUID,
    action: AdminActionType,
    reason: str | None = None,
) -> None:
    parts = [
        f"[ADMIN {kind}]",
        f"timestamp={_format_timestamp()}",
        f"admin={admin_id}",
        f"{target_label}={target_id}",
        f"action={action.value}",
    ]
    if reason:
        parts.append(f'reason="{reason}"')
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(" ".join(parts) + "\n")


def _create_action_record(
    db: Session,
    *,
    admin_id: UUID,
    target_id: UUID,
    action_type: AdminActionType,
    description: str | None,
) -> AdminAction:
    action = AdminAction(
        admin_id=admin_id,
        target_id=target_id,
        action_type=action_type,
        description=description,
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


async def block_or_unblock_user(
    db: Session,
    *,
    admin: User,
    target: User,
    blocked: bool,
    reason: str | None = None,
) -> AdminAction:
    target.is_active = not blocked
    action_type = AdminActionType.BLOCK_USER if blocked else AdminActionType.UNBLOCK_USER
    description = reason or ("Пользователь заблокирован" if blocked else "Пользователь разблокирован")

    action = _create_action_record(
        db,
        admin_id=admin.id,
        target_id=target.id,
        action_type=action_type,
        description=description,
    )

    _append_log(
        kind="ACTION",
        admin_id=admin.id,
        target_label="user",
        target_id=target.id,
        action=action_type,
        reason=reason,
    )

    title = "Аккаунт заблокирован" if blocked else "Аккаунт разблокирован"
    content = reason or (
        "Администратор ограничил ваш доступ." if blocked else "Доступ к платформе восстановлен."
    )
    await create_notification(
        db,
        user_id=target.id,
        notification_type="moderation",
        title=title,
        content=content,
        send_telegram=False,
    )
    return action


async def block_or_unblock_campaign(
    db: Session,
    *,
    admin: User,
    campaign: Campaign,
    blocked: bool,
    reason: str | None = None,
) -> AdminAction:
    campaign.is_blocked = blocked
    action_type = AdminActionType.BLOCK_CAMPAIGN if blocked else AdminActionType.UNBLOCK_CAMPAIGN
    description = reason or (
        "Кампания заблокирована модератором" if blocked else "Кампания восстановлена после модерации"
    )

    action = _create_action_record(
        db,
        admin_id=admin.id,
        target_id=campaign.id,
        action_type=action_type,
        description=description,
    )

    _append_log(
        kind="ACTION",
        admin_id=admin.id,
        target_label="campaign",
        target_id=campaign.id,
        action=action_type,
        reason=reason,
    )

    title = "Кампания заблокирована" if blocked else "Кампания разблокирована"
    content = reason or (
        "Модерация ограничила кампанию за нарушения." if blocked else "Кампания доступна снова."
    )

    await create_notification(
        db,
        user_id=campaign.brand_id,
        notification_type="moderation",
        title=title,
        content=content,
        send_telegram=False,
    )
    return action


async def send_warning(
    db: Session,
    *,
    admin: User,
    target: User,
    message: str,
) -> AdminAction:
    description = message.strip()
    action = _create_action_record(
        db,
        admin_id=admin.id,
        target_id=target.id,
        action_type=AdminActionType.WARNING,
        description=description,
    )

    _append_log(
        kind="WARNING",
        admin_id=admin.id,
        target_label="user",
        target_id=target.id,
        action=AdminActionType.WARNING,
        reason=message,
    )

    await create_notification(
        db,
        user_id=target.id,
        notification_type="moderation_warning",
        title="Предупреждение от модератора",
        content=message,
        send_telegram=False,
    )
    return action
