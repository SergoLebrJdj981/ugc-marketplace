"""Admin moderation endpoints for managing users and campaigns."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_session, require_admin
from app.models import AdminAction, AdminActionType, AdminLevel, Campaign, CampaignStatus, User
from app.schemas import (
    AdminActionRead,
    ModerationCampaign,
    ModerationCampaignActionResponse,
    ModerationCampaignsResponse,
    ModerationLogsResponse,
    ModerationToggleRequest,
    ModerationUser,
    ModerationUserActionResponse,
    ModerationUsersResponse,
    ModerationWarningRequest,
    ModerationWarningResponse,
)
from app.services.moderation import (
    block_or_unblock_campaign,
    block_or_unblock_user,
    send_warning,
)

router = APIRouter(prefix="/admin/moderation", tags=["Admin Moderation"])

LevelOrder = {
    AdminLevel.NONE: 0,
    AdminLevel.ADMIN_LEVEL_1: 1,
    AdminLevel.ADMIN_LEVEL_2: 2,
    AdminLevel.ADMIN_LEVEL_3: 3,
}


def _user_to_schema(user: User) -> ModerationUser:
    return ModerationUser(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        admin_level=user.admin_level,
        is_active=user.is_active,
        status="blocked" if not user.is_active else "active",
        created_at=user.created_at,
    )


def _campaign_to_schema(campaign: Campaign) -> ModerationCampaign:
    if campaign.is_blocked:
        moderation_state = "blocked"
    elif campaign.status == CampaignStatus.PAUSED:
        moderation_state = "under_review"
    else:
        moderation_state = "active"
    brand_name = campaign.brand.full_name if campaign.brand else None
    return ModerationCampaign(
        id=campaign.id,
        title=campaign.title,
        status=campaign.status,
        is_blocked=campaign.is_blocked,
        moderation_state=moderation_state,
        brand_id=campaign.brand_id,
        brand_name=brand_name,
        created_at=campaign.created_at,
    )


@router.get("/users", response_model=ModerationUsersResponse, status_code=status.HTTP_200_OK)
def list_users(
    *,
    db: Annotated[Session, Depends(get_session)],
    _: Annotated[User, Depends(require_admin(AdminLevel.ADMIN_LEVEL_1))],
    role: str | None = Query(default=None, description="Фильтр по роли пользователя"),
    active: bool | None = Query(default=None, description="Фильтр по флагу активности"),
    status_filter: str | None = Query(default=None, alias="status", description="Фильтр по статусу модерации"),
) -> ModerationUsersResponse:
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if active is not None:
        query = query.filter(User.is_active.is_(active))
    if status_filter:
        if status_filter == "blocked":
            query = query.filter(User.is_active.is_(False))
        elif status_filter == "active":
            query = query.filter(User.is_active.is_(True))

    users = query.order_by(User.created_at.desc()).all()
    items = [_user_to_schema(user) for user in users]
    return ModerationUsersResponse(total=len(items), items=items)


@router.get("/campaigns", response_model=ModerationCampaignsResponse, status_code=status.HTTP_200_OK)
def list_campaigns(
    *,
    db: Annotated[Session, Depends(get_session)],
    _: Annotated[User, Depends(require_admin(AdminLevel.ADMIN_LEVEL_1))],
    status_filter: CampaignStatus | None = Query(default=None, alias="status", description="Статус кампании"),
    blocked: bool | None = Query(default=None, description="Фильтр по признаку блокировки"),
    brand_id: UUID | None = Query(default=None, description="Фильтр по бренду"),
) -> ModerationCampaignsResponse:
    query = db.query(Campaign)
    if status_filter:
        query = query.filter(Campaign.status == status_filter)
    if blocked is not None:
        query = query.filter(Campaign.is_blocked.is_(blocked))
    if brand_id:
        query = query.filter(Campaign.brand_id == brand_id)

    campaigns = query.order_by(Campaign.created_at.desc()).all()
    items = [_campaign_to_schema(campaign) for campaign in campaigns]
    return ModerationCampaignsResponse(total=len(items), items=items)


@router.patch(
    "/user/{user_id}/block",
    response_model=ModerationUserActionResponse,
    status_code=status.HTTP_200_OK,
)
async def toggle_user_block(
    user_id: UUID,
    payload: ModerationToggleRequest,
    *,
    db: Annotated[Session, Depends(get_session)],
    admin: Annotated[User, Depends(require_admin(AdminLevel.ADMIN_LEVEL_1))],
) -> ModerationUserActionResponse:
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    if target.id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя блокировать свой аккаунт")
    if LevelOrder.get(target.admin_level, 0) > LevelOrder.get(admin.admin_level, 0):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для операции")

    action = await block_or_unblock_user(
        db,
        admin=admin,
        target=target,
        blocked=payload.blocked,
        reason=payload.reason,
    )
    return ModerationUserActionResponse(
        user=_user_to_schema(target),
        action=AdminActionRead.model_validate(action),
    )


@router.patch(
    "/campaign/{campaign_id}/block",
    response_model=ModerationCampaignActionResponse,
    status_code=status.HTTP_200_OK,
)
async def toggle_campaign_block(
    campaign_id: UUID,
    payload: ModerationToggleRequest,
    *,
    db: Annotated[Session, Depends(get_session)],
    admin: Annotated[User, Depends(require_admin(AdminLevel.ADMIN_LEVEL_1))],
) -> ModerationCampaignActionResponse:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Кампания не найдена")

    action = await block_or_unblock_campaign(
        db,
        admin=admin,
        campaign=campaign,
        blocked=payload.blocked,
        reason=payload.reason,
    )
    return ModerationCampaignActionResponse(
        campaign=_campaign_to_schema(campaign),
        action=AdminActionRead.model_validate(action),
    )


@router.post(
    "/warning",
    response_model=ModerationWarningResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_warning(
    payload: ModerationWarningRequest,
    *,
    db: Annotated[Session, Depends(get_session)],
    admin: Annotated[User, Depends(require_admin(AdminLevel.ADMIN_LEVEL_1))],
) -> ModerationWarningResponse:
    target = db.get(User, payload.user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    if LevelOrder.get(target.admin_level, 0) > LevelOrder.get(admin.admin_level, 0):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для операции")

    action = await send_warning(db, admin=admin, target=target, message=payload.message)
    return ModerationWarningResponse(
        user=_user_to_schema(target),
        action=AdminActionRead.model_validate(action),
    )


@router.get(
    "/logs",
    response_model=ModerationLogsResponse,
    status_code=status.HTTP_200_OK,
)
def list_logs(
    *,
    db: Annotated[Session, Depends(get_session)],
    _: Annotated[User, Depends(require_admin(AdminLevel.ADMIN_LEVEL_1))],
    admin_id: UUID | None = Query(default=None),
    target_id: UUID | None = Query(default=None),
    action_type: AdminActionType | None = Query(default=None),
) -> ModerationLogsResponse:
    query = db.query(AdminAction)
    if admin_id:
        query = query.filter(AdminAction.admin_id == admin_id)
    if target_id:
        query = query.filter(AdminAction.target_id == target_id)
    if action_type:
        query = query.filter(AdminAction.action_type == action_type)

    actions = query.order_by(AdminAction.created_at.desc()).limit(200).all()
    items = [AdminActionRead.model_validate(action) for action in actions]
    return ModerationLogsResponse(total=len(items), items=items)
