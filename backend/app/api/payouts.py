"""Payout API endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Payout, User
from app.schemas import WithdrawRequest, WithdrawResponse
from app.services.escrow import EscrowError, EscrowPermissionError, withdraw_payout

router = APIRouter(prefix="/payouts")

SessionDep = Annotated[Session, Depends(get_db)]


@router.post("/withdraw", response_model=WithdrawResponse, status_code=status.HTTP_200_OK)
def withdraw(
    payload: WithdrawRequest,
    db: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
) -> WithdrawResponse:
    payout = db.get(Payout, payload.payout_id)
    if not payout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Выплата не найдена")

    try:
        updated_payout = withdraw_payout(db, payout=payout, actor=current_user)
    except EscrowPermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except EscrowError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    db.commit()
    db.refresh(updated_payout)
    return WithdrawResponse(payout_id=updated_payout.id, status=updated_payout.status, amount=updated_payout.amount)
