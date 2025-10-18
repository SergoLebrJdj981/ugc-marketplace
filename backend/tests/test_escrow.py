from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import (
    AdminLevel,
    Campaign,
    CampaignStatus,
    Payment,
    PaymentStatus,
    Payout,
    PayoutStatus,
    Transaction,
    TransactionType,
    User,
)

LOGS_DIR = Path(__file__).resolve().parents[2] / 'logs'


def register_user(client: TestClient, email: str, role: str) -> tuple[str, str]:
    response = client.post(
        '/api/auth/register',
        json={
            'email': email,
            'password': 'Secret123!',
            'full_name': f'{role.title()} User',
            'role': role,
        },
    )
    assert response.status_code == 201
    data = response.json()
    return data['access_token'], data['user']['id']


def test_escrow_deposit_release_withdraw(client: TestClient, db_session: Session) -> None:
    columns = {row[1] for row in db_session.execute(text("PRAGMA table_info(users)"))}
    assert 'admin_level' in columns
    brand_token, brand_id = register_user(client, 'brand@test.dev', 'brand')
    creator_token, creator_id = register_user(client, 'creator@test.dev', 'creator')
    admin_token, admin_id = register_user(client, 'admin@test.dev', 'admin')

    admin = db_session.get(User, UUID(admin_id))
    assert admin is not None
    admin.admin_level = AdminLevel.ADMIN_LEVEL_3
    db_session.commit()

    campaign = Campaign(
        brand_id=UUID(brand_id),
        title='Escrow Campaign',
        budget=Decimal('100000'),
        status=CampaignStatus.ACTIVE,
    )
    db_session.add(campaign)
    db_session.commit()

    deposit_response = client.post(
        '/api/payments/deposit',
        headers={'Authorization': f'Bearer {brand_token}'},
        json={'amount': 15000},
    )
    assert deposit_response.status_code == 201
    payment_id = deposit_response.json()['id']

    payment = db_session.get(Payment, UUID(payment_id))
    assert payment is not None
    assert payment.status in {PaymentStatus.HOLD, PaymentStatus.RESERVED}
    transactions = db_session.query(Transaction).filter(Transaction.user_id == UUID(brand_id)).all()
    assert any(txn.type == TransactionType.DEPOSIT for txn in transactions)

    payments_log = (LOGS_DIR / 'payments.log').read_text(encoding='utf-8')
    assert 'deposit' in payments_log
    bank_log = (LOGS_DIR / 'bank_webhooks.log').read_text(encoding='utf-8')
    assert 'deposit_confirmed' in bank_log

    release_response = client.patch(
        '/api/payments/release',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'payment_id': payment_id, 'creator_id': creator_id, 'campaign_id': str(campaign.id)},
    )
    assert release_response.status_code == 200
    release_data = release_response.json()
    payout_id = release_data['payout_id']
    assert float(release_data['fee']) > 0
    assert float(release_data['payout_amount']) > 0

    db_session.expire_all()
    payment = db_session.get(Payment, UUID(payment_id))
    assert payment is not None
    assert payment.status == PaymentStatus.RELEASED
    payout = db_session.get(Payout, UUID(payout_id))
    assert payout is not None
    assert payout.status == PayoutStatus.RELEASED

    transactions = db_session.query(Transaction).filter(Transaction.user_id == UUID(brand_id)).all()
    types = {txn.type for txn in transactions}
    assert TransactionType.FEE in types
    assert TransactionType.RELEASE in types

    release_log = (LOGS_DIR / 'payments.log').read_text(encoding='utf-8')
    assert 'platform_fee_payout' in release_log

    withdraw_response = client.post(
        '/api/payouts/withdraw',
        headers={'Authorization': f'Bearer {creator_token}'},
        json={'payout_id': payout_id},
    )
    assert withdraw_response.status_code == 200

    db_session.expire_all()
    payout = db_session.get(Payout, UUID(payout_id))
    assert payout is not None
    assert payout.status == PayoutStatus.WITHDRAWN
    payment = db_session.get(Payment, UUID(payment_id))
    assert payment is not None
    assert payment.status == PaymentStatus.PAID

    creator_transactions = db_session.query(Transaction).filter(Transaction.user_id == UUID(creator_id)).all()
    assert any(txn.type == TransactionType.WITHDRAW for txn in creator_transactions)

    withdraw_log = (LOGS_DIR / 'payments.log').read_text(encoding='utf-8')
    assert 'WITHDRAWN' in withdraw_log or 'withdrawn' in withdraw_log


def test_platform_fee_endpoints(client: TestClient, db_session: Session) -> None:
    admin_token, admin_id = register_user(client, 'fee-admin@test.dev', 'admin')

    admin = db_session.get(User, UUID(admin_id))
    assert admin is not None
    admin.admin_level = AdminLevel.ADMIN_LEVEL_3
    db_session.commit()

    get_response = client.get(
        '/api/admin/settings/platform_fee',
        headers={'Authorization': f'Bearer {admin_token}'},
    )
    assert get_response.status_code == 200
    current_value = float(get_response.json()['value'])
    assert 0 < current_value < 1

    patch_response = client.patch(
        '/api/admin/settings/platform_fee',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'value': 0.12},
    )
    assert patch_response.status_code == 200
    assert float(patch_response.json()['value']) == 0.12

    fees_log = (LOGS_DIR / 'fees.log').read_text(encoding='utf-8')
    assert 'platform_fee updated' in fees_log
