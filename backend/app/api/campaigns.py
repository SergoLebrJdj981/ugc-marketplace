"""Campaign endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_db
from app.models import Campaign, CampaignStatus, User, UserRole
from app.schemas import CampaignCreate, CampaignListResponse, CampaignRead
from app.services.notifications import schedule_notification

router = APIRouter(prefix="/campaigns")

SessionDep = Annotated[Session, Depends(get_db)]


@router.get("", response_model=CampaignListResponse)
def list_campaigns(
    *,
    db: SessionDep,
    status_filter: CampaignStatus | None = Query(default=None, alias="status"),
    brand_id: UUID | None = None,
) -> CampaignListResponse:
    """Return campaigns filtered by status and/or brand."""

    stmt: Select[tuple[Campaign]] = select(Campaign)
    if status_filter:
        stmt = stmt.where(Campaign.status == status_filter)
    if brand_id:
        stmt = stmt.where(Campaign.brand_id == brand_id)

    items = list(db.scalars(stmt).all())
    return CampaignListResponse(items=[CampaignRead.model_validate(item) for item in items], total=len(items))


@router.post("", response_model=CampaignRead, status_code=status.HTTP_201_CREATED)
def create_campaign(
    *,
    db: SessionDep,
    payload: CampaignCreate,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
) -> CampaignRead:
    """Create a new campaign."""

    resolved_brand_id = payload.brand_id
    if resolved_brand_id is None:
        if current_user.role != UserRole.BRAND:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only brands can create campaigns")
        resolved_brand_id = current_user.id
    elif current_user.role == UserRole.BRAND and resolved_brand_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brands may only create campaigns for their own account",
        )

    brand = db.get(User, resolved_brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

    campaign = Campaign(
        title=payload.title,
        description=payload.description,
        budget=payload.budget,
        currency=payload.currency,
        brand_id=resolved_brand_id,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    schedule_notification(
        background_tasks,
        user_id=resolved_brand_id,
        notification_type="campaign.created",
        message=f"Campaign '{campaign.title}' created",
    )
    return CampaignRead.model_validate(campaign)
