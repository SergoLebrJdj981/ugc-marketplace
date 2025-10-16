"""Campaign endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_db
from app.models import Campaign, CampaignStatus
from app.schemas import CampaignCreate, CampaignListResponse, CampaignRead

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
def create_campaign(*, db: SessionDep, payload: CampaignCreate) -> CampaignRead:
    """Create a new campaign."""

    campaign = Campaign(
        title=payload.title,
        description=payload.description,
        budget=payload.budget,
        currency=payload.currency,
        brand_id=payload.brand_id,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return CampaignRead.model_validate(campaign)
