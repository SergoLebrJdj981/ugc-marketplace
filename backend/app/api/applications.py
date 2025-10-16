"""Application endpoints."""

from __future__ import annotations

from typing import Annotated

from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_db
from app.models import Application, Campaign, User
from app.schemas import ApplicationCreate, ApplicationRead

router = APIRouter(prefix="/applications")

SessionDep = Annotated[Session, Depends(get_db)]


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(*, db: SessionDep, payload: ApplicationCreate) -> ApplicationRead:
    """Create a creator application for a campaign."""

    campaign = db.scalar(select(Campaign).where(Campaign.id == payload.campaign_id))
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    creator = db.scalar(select(User).where(User.id == payload.creator_id))
    if not creator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator not found")

    application = Application(
        campaign_id=payload.campaign_id,
        creator_id=payload.creator_id,
        pitch=payload.pitch,
        proposed_budget=payload.proposed_budget,
        message=payload.message,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return ApplicationRead.model_validate(application)
