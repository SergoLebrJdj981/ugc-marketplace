"""Brand management endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Brand, User, UserRole
from app.schemas import BrandCreate, BrandRead

router = APIRouter(prefix="/brands")


@router.post("", response_model=BrandRead, status_code=status.HTTP_201_CREATED)
def create_brand(
    *,
    payload: BrandCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BrandRead:
    """Create a brand profile for the authenticated brand user."""

    if current_user.role != UserRole.BRAND:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only brand users can create profiles")

    existing = db.get(Brand, current_user.id)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Brand profile already exists")

    brand = Brand(id=current_user.id, name=payload.name, description=payload.description)
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return BrandRead.model_validate(brand)
