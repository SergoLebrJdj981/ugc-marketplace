"""Escrow payment API endpoints."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin
from app.models import AdminLevel, Campaign, Payment, User
from app.schemas import DepositRequest, DepositResponse, ReleaseRequest, ReleaseResponse
from app.services.escrow import (
    EscrowError,
    create_deposit as escrow_create_deposit,
    get_platform_fee_deposit,
    get_platform_fee_payout,
    handle_bank_webhook,
    release_payment,
)

router = APIRouter(prefix="/payments")

SessionDep = Annotated[Session, Depends(get_db)]


@router.post("/deposit", response_model=DepositResponse, status_code=status.HTTP_201_CREATED)
def create_deposit(
    payload: DepositRequest,
    db: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
) -> DepositResponse:
    if current_user.role != "brand":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только бренды могут пополнять баланс")

    requested_amount = Decimal(payload.amount)
    try:
        payment = escrow_create_deposit(db, current_user, requested_amount)
    except EscrowError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    handle_bank_webhook(
        db,
        event="deposit_confirmed",
        payload={"payment_id": str(payment.id), "amount": str(requested_amount), "brand_id": str(current_user.id)},
    )
    db.commit()
    db.refresh(payment)
    deposit_fee_rate = get_platform_fee_deposit(db)
    payout_fee_rate = get_platform_fee_payout(db)
    return DepositResponse(
        id=payment.id,
        brand_id=payment.brand_id,
        requested_amount=requested_amount,
        amount=payment.amount,
        deposit_fee=payment.deposit_fee,
        payout_fee_rate=payout_fee_rate,
        status=payment.status,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
    )


@router.patch(
    "/release",
    response_model=ReleaseResponse,
    status_code=status.HTTP_200_OK,
)
def release_funds(
    payload: ReleaseRequest,
    db: SessionDep,
    _: Annotated[User, Depends(require_admin(AdminLevel.ADMIN_LEVEL_2))],
) -> ReleaseResponse:
    payment = db.get(Payment, payload.payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Платёж не найден")

    creator = db.get(User, payload.creator_id)
    if not creator or creator.role != "creator":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Некорректный креатор")

    campaign = db.get(Campaign, payload.campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Кампания не найдена")

    try:
        updated_payment, payout, fee_amount, payout_amount, platform_fee_payout = release_payment(
            db,
            payment=payment,
            creator=creator,
            campaign_id=campaign.id,
        )
    except EscrowError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    db.commit()
    db.refresh(updated_payment)
    db.refresh(payout)

    return ReleaseResponse(
        payment_id=updated_payment.id,
        payout_id=payout.id,
        status=updated_payment.status,
        payout_status=payout.status,
        fee=fee_amount,
        payout_amount=payout_amount,
        platform_fee_payout=platform_fee_payout,
    )
