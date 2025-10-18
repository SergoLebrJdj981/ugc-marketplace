from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import AdminLevel, Campaign, CampaignStatus, Payment, PaymentStatus, User


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
    response.raise_for_status()
    data = response.json()
    return data['access_token'], data['user']['id']


def promote_admin(db_session: Session, admin_id: str, level: AdminLevel = AdminLevel.ADMIN_LEVEL_3) -> None:
    admin = db_session.get(User, UUID(admin_id))
    assert admin is not None
    admin.admin_level = level
    db_session.commit()


def create_campaign(db_session: Session, brand_id: str) -> Campaign:
    campaign = Campaign(
        brand_id=UUID(brand_id),
        title='Fees Campaign',
        budget=Decimal('50000'),
        status=CampaignStatus.ACTIVE,
    )
    db_session.add(campaign)
    db_session.commit()
    return campaign


def test_dual_platform_fees_flow(client: TestClient, db_session: Session) -> None:
    brand_token, brand_id = register_user(client, 'dual-fees-brand@test.dev', 'brand')
    creator_token, creator_id = register_user(client, 'dual-fees-creator@test.dev', 'creator')
    admin_token, admin_id = register_user(client, 'dual-fees-admin@test.dev', 'admin')

    promote_admin(db_session, admin_id)
    campaign = create_campaign(db_session, brand_id)

    headers = {'Authorization': f'Bearer {admin_token}'}
    assert client.patch('/api/admin/settings/platform_fee_deposit', headers=headers, json={'value': 0.10}).status_code == 200
    assert client.patch('/api/admin/settings/platform_fee_payout', headers=headers, json={'value': 0.15}).status_code == 200

    deposit_headers = {'Authorization': f'Bearer {brand_token}'}
    deposit_response = client.post(
        '/api/payments/deposit',
        headers=deposit_headers,
        json={'amount': 10000},
    )
    assert deposit_response.status_code == 201
    payment_id = deposit_response.json()['id']

    payment = db_session.get(Payment, UUID(payment_id))
    assert payment is not None
    assert payment.deposit_fee == Decimal('1000.00')
    assert payment.amount == Decimal('9000.00')
    assert payment.status in {PaymentStatus.RESERVED, PaymentStatus.HOLD}

    # Deposit tailored to net 1 000 ₽ after 10% commission
    secondary_deposit = client.post(
        '/api/payments/deposit',
        headers=deposit_headers,
        json={'amount': 1111.11},
    )
    assert secondary_deposit.status_code == 201
    payout_payment_id = secondary_deposit.json()['id']

    payout_payment = db_session.get(Payment, UUID(payout_payment_id))
    assert payout_payment is not None
    assert payout_payment.amount == Decimal('1000.00')
    assert payout_payment.deposit_fee == Decimal('111.11')

    release_headers = {'Authorization': f'Bearer {admin_token}'}
    release_response = client.patch(
        '/api/payments/release',
        headers=release_headers,
        json={
            'payment_id': payout_payment_id,
            'creator_id': creator_id,
            'campaign_id': str(campaign.id),
        },
    )
    assert release_response.status_code == 200
    release_payload = release_response.json()
    assert Decimal(release_payload['fee']) == Decimal('150.00')
    assert Decimal(release_payload['payout_amount']) == Decimal('850.00')
    assert Decimal(release_payload['platform_fee_payout']) == Decimal('0.15')

    db_session.expire_all()
    payout_payment = db_session.get(Payment, UUID(payout_payment_id))
    assert payout_payment is not None
    assert payout_payment.status == PaymentStatus.RELEASED
    assert payout_payment.fee == Decimal('150.00')

    payout_headers = {'Authorization': f'Bearer {creator_token}'}
    withdraw_response = client.post(
        '/api/payouts/withdraw',
        headers=payout_headers,
        json={'payout_id': release_payload['payout_id']},
    )
    assert withdraw_response.status_code == 200
