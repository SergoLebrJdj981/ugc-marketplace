"""Escrow domain services."""

from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Any
from uuid import UUID

from loguru import logger
from sqlalchemy.orm import Session

from app.models import (
    Payment,
    PaymentStatus,
    Payout,
    PayoutStatus,
    SystemSetting,
    Transaction,
    TransactionType,
    User,
)

PLATFORM_FEE_KEY = "platform_fee"
PLATFORM_FEE_DEPOSIT_KEY = "platform_fee_deposit"
PLATFORM_FEE_PAYOUT_KEY = "platform_fee_payout"
DEFAULT_FEE_VALUE = Decimal("0.10")
DEFAULT_FEE_DESCRIPTION = "Размер комиссии платформы"
DEFAULT_DEPOSIT_DESCRIPTION = "Комиссия платформы при депозите"
DEFAULT_PAYOUT_DESCRIPTION = "Комиссия платформы при выплатах"
_TWO_PLACES = Decimal("0.01")


class EscrowError(Exception):
    """Base exception for escrow operations."""


class EscrowPermissionError(EscrowError):
    """Raised when an operation is not allowed."""


def _quantize(amount: Decimal) -> Decimal:
    return amount.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)


def _log_payments(message: str, *args: object) -> None:
    logger.bind(channel="payments").info(message, *args)


def _log_bank(event: str, payload: dict[str, Any]) -> None:
    logger.bind(channel="bank_webhooks").info(
        "[BANK] event={} payload={}",
        event,
        json.dumps(payload, ensure_ascii=False),
    )


def _log_fee_change(message: str) -> None:
    logger.bind(channel="fees").info(message)


def get_platform_fee(session: Session) -> Decimal:
    setting = _ensure_setting_default(
        session,
        key=PLATFORM_FEE_KEY,
        fallback=DEFAULT_FEE_VALUE,
        description=DEFAULT_FEE_DESCRIPTION,
    )
    return Decimal(setting.value)  # type: ignore[arg-type]


def get_platform_fee_deposit(session: Session) -> Decimal:
    fallback = get_platform_fee(session)
    setting = _ensure_setting_default(
        session,
        key=PLATFORM_FEE_DEPOSIT_KEY,
        fallback=fallback,
        description=DEFAULT_DEPOSIT_DESCRIPTION,
    )
    return Decimal(setting.value or fallback)  # type: ignore[arg-type]


def get_platform_fee_payout(session: Session) -> Decimal:
    fallback = get_platform_fee(session)
    setting = _ensure_setting_default(
        session,
        key=PLATFORM_FEE_PAYOUT_KEY,
        fallback=fallback,
        description=DEFAULT_PAYOUT_DESCRIPTION,
    )
    return Decimal(setting.value or fallback)  # type: ignore[arg-type]


def set_platform_fee(session: Session, value: Decimal, actor: User | None = None) -> SystemSetting:
    return _set_platform_setting(
        session,
        key=PLATFORM_FEE_KEY,
        label="platform_fee",
        description=DEFAULT_FEE_DESCRIPTION,
        value=value,
        actor=actor,
        fallback=DEFAULT_FEE_VALUE,
    )


def set_platform_fee_deposit(session: Session, value: Decimal, actor: User | None = None) -> SystemSetting:
    fallback = get_platform_fee(session)
    return _set_platform_setting(
        session,
        key=PLATFORM_FEE_DEPOSIT_KEY,
        label="platform_fee_deposit",
        description=DEFAULT_DEPOSIT_DESCRIPTION,
        value=value,
        actor=actor,
        fallback=fallback,
    )


def set_platform_fee_payout(session: Session, value: Decimal, actor: User | None = None) -> SystemSetting:
    fallback = get_platform_fee(session)
    return _set_platform_setting(
        session,
        key=PLATFORM_FEE_PAYOUT_KEY,
        label="platform_fee_payout",
        description=DEFAULT_PAYOUT_DESCRIPTION,
        value=value,
        actor=actor,
        fallback=fallback,
    )


def create_deposit(session: Session, brand: User, amount: Decimal) -> Payment:
    amount = _quantize(amount)
    if amount <= Decimal("0.00"):
        raise EscrowError("Deposit amount must be positive")

    deposit_rate = get_platform_fee_deposit(session)
    payout_rate = get_platform_fee_payout(session)
    deposit_fee_amount = _quantize(amount * deposit_rate)
    net_amount = _quantize(amount - deposit_fee_amount)
    if net_amount <= Decimal("0.00"):
        raise EscrowError("Deposit amount is fully consumed by commissions")

    payment = Payment(
        brand_id=brand.id,
        amount=net_amount,
        deposit_fee=deposit_fee_amount,
        fee=Decimal("0.00"),
        status=PaymentStatus.HOLD,
    )
    session.add(payment)
    session.flush()

    transaction = Transaction(
        user_id=brand.id,
        type=TransactionType.DEPOSIT,
        amount=amount,
        reference_id=payment.id,
        reference_type="payment",
        description=f"Deposit initiated by {brand.email}",
    )
    session.add(transaction)
    if deposit_fee_amount > Decimal("0.00"):
        session.add(
            Transaction(
                user_id=brand.id,
                type=TransactionType.FEE,
                amount=deposit_fee_amount,
                reference_id=payment.id,
                reference_type="payment",
                description=f"Deposit fee retained for payment {payment.id}",
            )
        )

    _log_payments(
        "[ESCROW] brand={} deposit={:.2f} fee_deposit={:.2f}% payout_fee={:.2f}%",
        brand.id,
        float(amount),
        float(deposit_rate * 100),
        float(payout_rate * 100),
    )
    _log_bank(
        "deposit_hold",
        {
            "payment_id": str(payment.id),
            "amount": str(amount),
            "brand_id": str(brand.id),
            "deposit_fee": str(deposit_fee_amount),
        },
    )
    return payment


def release_payment(
    session: Session,
    *,
    payment: Payment,
    creator: User,
    campaign_id: UUID,
) -> tuple[Payment, Payout, Decimal, Decimal, Decimal]:
    if payment.status not in {PaymentStatus.HOLD, PaymentStatus.RESERVED}:
        raise EscrowError("Payment is not available for release")

    payout_rate = get_platform_fee_payout(session)
    fee_amount = _quantize(payment.amount * payout_rate)
    payout_amount = _quantize(payment.amount - fee_amount)

    payment.status = PaymentStatus.RELEASED
    payment.fee = fee_amount

    payout = Payout(
        creator_id=creator.id,
        campaign_id=campaign_id,
        payment_id=payment.id,
        amount=payout_amount,
        status=PayoutStatus.RELEASED,
    )
    session.add(payout)
    session.flush()

    release_txn = Transaction(
        user_id=payment.brand_id,
        type=TransactionType.RELEASE,
        amount=payout_amount,
        reference_id=payment.id,
        reference_type="payment",
        description=f"Payout released to {creator.email}",
    )
    fee_txn = Transaction(
        user_id=payment.brand_id,
        type=TransactionType.FEE,
        amount=fee_amount,
        reference_id=payment.id,
        reference_type="payment",
        description=f"Platform fee retained for payment {payment.id}",
    )
    session.add_all([release_txn, fee_txn])

    _log_payments(
        "[ESCROW] platform_fee_payout={:.2f}% → fee={:.2f} payout={:.2f}",
        float(payout_rate * 100),
        float(fee_amount),
        float(payout_amount),
    )
    _log_payments(
        "[ESCROW] payout to creator={} amount={:.2f} status={}",
        creator.id,
        float(payout_amount),
        payout.status.value.upper(),
    )
    _log_bank(
        "payout_released",
        {
            "payment_id": str(payment.id),
            "payout_id": str(payout.id),
            "amount": str(payout_amount),
            "fee": str(fee_amount),
        },
    )
    return payment, payout, fee_amount, payout_amount, payout_rate


def withdraw_payout(session: Session, *, payout: Payout, actor: User) -> Payout:
    if payout.creator_id != actor.id:
        raise EscrowPermissionError("Нельзя выводить чужую выплату")
    if payout.status == PayoutStatus.WITHDRAWN:
        raise EscrowError("Выплата уже выведена")

    payout.status = PayoutStatus.WITHDRAWN
    session.flush()

    transaction = Transaction(
        user_id=payout.creator_id,
        type=TransactionType.WITHDRAW,
        amount=payout.amount,
        reference_id=payout.id,
        reference_type="payout",
        description=f"Payout withdrawn by {actor.email}",
    )
    session.add(transaction)

    if payout.payment:
        payout.payment.status = PaymentStatus.PAID

    _log_payments(
        "[ESCROW] payout to creator={} amount={:.2f} status={}",
        actor.id,
        float(payout.amount),
        payout.status.value.upper(),
    )
    _log_bank(
        "withdraw_processed",
        {"payout_id": str(payout.id), "amount": str(payout.amount), "creator_id": str(actor.id)},
    )
    return payout


def handle_bank_webhook(session: Session, *, event: str, payload: dict[str, Any]) -> dict[str, Any]:
    _log_bank(event, payload)

    if event == "deposit_confirmed":
        payment_id = payload.get("payment_id")
        if payment_id:
            payment = session.get(Payment, UUID(str(payment_id)))
            if payment and payment.status == PaymentStatus.HOLD:
                payment.status = PaymentStatus.RESERVED
                session.flush()
                _log_payments(
                    "[ESCROW] bank confirmed deposit payment={} status={}",
                    payment.id,
                    payment.status.value.upper(),
                )
    elif event == "payout_paid":
        payout_id = payload.get("payout_id")
        if payout_id:
            payout = session.get(Payout, UUID(str(payout_id)))
            if payout and payout.status != PayoutStatus.WITHDRAWN:
                payout.status = PayoutStatus.WITHDRAWN
                if payout.payment:
                    payout.payment.status = PaymentStatus.PAID
                session.flush()
                _log_payments(
                    "[ESCROW] bank marked payout={} status={}",
                    payout.id,
                    payout.status.value.upper(),
                )
    return {"status": "accepted", "event": event}


def _ensure_setting_default(
    session: Session,
    *,
    key: str,
    fallback: Decimal,
    description: str,
) -> SystemSetting:
    setting = session.query(SystemSetting).filter(SystemSetting.key == key).one_or_none()
    if setting is None:
        setting = SystemSetting(key=key, value=fallback, description=description)
        session.add(setting)
        session.flush()
        return setting

    updated = False
    if setting.value is None:
        setting.value = fallback
        updated = True
    if not setting.description:
        setting.description = description
        updated = True
    if updated:
        session.flush()
    return setting


def _set_platform_setting(
    session: Session,
    *,
    key: str,
    label: str,
    description: str,
    value: Decimal,
    actor: User | None,
    fallback: Decimal,
) -> SystemSetting:
    value = value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    setting = session.query(SystemSetting).filter(SystemSetting.key == key).one_or_none()
    previous_value = Decimal(fallback)
    if setting is None:
        setting = SystemSetting(key=key, value=value, description=description)
        session.add(setting)
    else:
        if setting.value is not None:
            previous_value = Decimal(setting.value)  # type: ignore[arg-type]
        setting.value = value
        if not setting.description:
            setting.description = description
    session.flush()

    actor_label = f" by {actor.email}" if actor else ""
    _log_fee_change(
        f"[ADMIN] {label} updated: {previous_value:.2%} → {value:.2%}{actor_label}"
    )
    return setting
