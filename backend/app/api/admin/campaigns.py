"""Admin endpoints for campaigns."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.models import Campaign, User
from app.models.enums import AdminLevel
from app.schemas import AdminCampaignStatusUpdate, CampaignRead
from app.services.admin_logs import log_admin_action

router = APIRouter()


@router.get("", response_model=list[CampaignRead])
def list_campaigns(
    *,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin(AdminLevel.ADMIN_LEVEL_1)),
) -> list[CampaignRead]:
    campaigns = db.query(Campaign).all()
    return [CampaignRead.model_validate(c) for c in campaigns]


@router.patch("/{campaign_id}/status", response_model=CampaignRead)
def update_campaign_status(
    *,
    campaign_id: UUID,
    payload: AdminCampaignStatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin(AdminLevel.ADMIN_LEVEL_1)),
) -> CampaignRead:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    campaign.status = payload.status
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    log_admin_action(db, str(admin_user.id), "update_campaign_status", str(campaign_id), metadata=payload.model_dump())
    return CampaignRead.model_validate(campaign)


@router.delete("/{campaign_id}")
def delete_campaign(
    *,
    campaign_id: UUID,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin(AdminLevel.ADMIN_LEVEL_3)),
) -> None:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    db.delete(campaign)
    db.commit()
    log_admin_action(db, str(admin_user.id), "delete_campaign", str(campaign_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
