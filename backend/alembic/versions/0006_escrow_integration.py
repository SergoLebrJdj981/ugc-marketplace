"""Escrow tables and platform fee setting."""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from uuid import uuid4
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006_escrow_integration"
down_revision: Union[str, Sequence[str], None] = "0005_add_telegram_links"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PAYMENT_STATUS = ("hold", "reserved", "released", "paid", "refunded")
PAYOUT_STATUS = ("pending", "released", "withdrawn")
TRANSACTION_TYPE = ("deposit", "reserve", "release", "withdraw", "fee")
ADMIN_LEVEL = ("none", "admin_level_1", "admin_level_2", "admin_level_3")


def upgrade() -> None:
    bind = op.get_bind()

    # Ensure admin_level column exists
    admin_level_enum = sa.Enum(*ADMIN_LEVEL, name="admin_level")
    admin_level_enum.create(bind, checkfirst=True)
    with op.batch_alter_table("users") as batch:
        batch.add_column(
            sa.Column("admin_level", admin_level_enum, nullable=False, server_default="none")
        )
    op.execute("UPDATE users SET admin_level = 'admin_level_3' WHERE role = 'admin'")

    # Drop legacy payments table/types if present
    op.execute("DROP TABLE IF EXISTS transactions CASCADE")
    op.execute("DROP TABLE IF EXISTS payouts CASCADE")
    op.execute("DROP TABLE IF EXISTS payments CASCADE")
    op.execute("DROP TABLE IF EXISTS system_settings CASCADE")
    op.execute("DROP TYPE IF EXISTS payment_status CASCADE")
    op.execute("DROP TYPE IF EXISTS payment_type CASCADE")

    payment_status_enum = sa.Enum(*PAYMENT_STATUS, name="payment_status")
    payout_status_enum = sa.Enum(*PAYOUT_STATUS, name="payout_status")
    transaction_type_enum = sa.Enum(*TRANSACTION_TYPE, name="transaction_type")
    payment_status_enum.create(bind, checkfirst=True)
    payout_status_enum.create(bind, checkfirst=True)
    transaction_type_enum.create(bind, checkfirst=True)

    op.create_table(
        "payments",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("brand_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("deposit_fee", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("fee", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("status", payment_status_enum, nullable=False, server_default="hold"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_payments_brand_id", "payments", ["brand_id"])

    op.create_table(
        "payouts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("creator_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("campaign_id", sa.String(length=36), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("payment_id", sa.String(length=36), sa.ForeignKey("payments.id", ondelete="SET NULL")),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", payout_status_enum, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_payouts_creator_id", "payouts", ["creator_id"])
    op.create_index("ix_payouts_campaign_id", "payouts", ["campaign_id"])

    op.create_table(
        "transactions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", transaction_type_enum, nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("reference_id", sa.String(length=36)),
        sa.Column("reference_type", sa.String(length=20)),
        sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])

    op.create_table(
        "system_settings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("key", sa.String(length=120), nullable=False, unique=True),
        sa.Column("value", sa.Numeric(8, 4), nullable=False, server_default="0"),
        sa.Column("description", sa.String(length=255)),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.execute(
        sa.text(
            "INSERT INTO system_settings (id, key, value, description) VALUES (:id, :key, :value, :description)"
        ),
        {
            "id": str(uuid4()),
            "key": "platform_fee",
            "value": Decimal("0.10"),
            "description": "10% комиссия платформы",
        },
    )
    op.execute(
        sa.text(
            "INSERT INTO system_settings (id, key, value, description) VALUES (:id, :key, :value, :description)"
        ),
        {
            "id": str(uuid4()),
            "key": "platform_fee_deposit",
            "value": Decimal("0.10"),
            "description": "Комиссия платформы при депозите (10%)",
        },
    )
    op.execute(
        sa.text(
            "INSERT INTO system_settings (id, key, value, description) VALUES (:id, :key, :value, :description)"
        ),
        {
            "id": str(uuid4()),
            "key": "platform_fee_payout",
            "value": Decimal("0.10"),
            "description": "Комиссия платформы при выплатах (10%)",
        },
    )

    with op.batch_alter_table("users") as batch:
        batch.alter_column("admin_level", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_column("admin_level")

    op.drop_table("transactions")
    op.drop_table("payouts")
    op.drop_table("system_settings")
    op.drop_table("payments")

    op.execute("DROP TYPE IF EXISTS transaction_type")
    op.execute("DROP TYPE IF EXISTS payout_status")
    op.execute("DROP TYPE IF EXISTS payment_status")
    op.execute("DROP TYPE IF EXISTS admin_level")
*** End of File
