"""Admin moderation action audit table."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0007_add_admin_actions"
down_revision: Union[str, Sequence[str], None] = "0006_escrow_integration"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ADMIN_ACTION_TYPES = (
    "block_user",
    "unblock_user",
    "block_campaign",
    "unblock_campaign",
    "warning",
)


def upgrade() -> None:
    bind = op.get_bind()

    admin_action_enum = sa.Enum(*ADMIN_ACTION_TYPES, name="admin_action_type")
    admin_action_enum.create(bind, checkfirst=True)

    op.create_table(
        "admin_actions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "admin_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("target_id", sa.String(length=36), nullable=False),
        sa.Column("action_type", admin_action_enum, nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_admin_actions_admin_id", "admin_actions", ["admin_id"])
    op.create_index("ix_admin_actions_target_id", "admin_actions", ["target_id"])

    op.add_column(
        "campaigns",
        sa.Column("is_blocked", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("campaigns", "is_blocked", server_default=None)


def downgrade() -> None:
    op.drop_column("campaigns", "is_blocked")

    op.drop_index("ix_admin_actions_target_id", table_name="admin_actions")
    op.drop_index("ix_admin_actions_admin_id", table_name="admin_actions")
    op.drop_table("admin_actions")

    admin_action_enum = sa.Enum(*ADMIN_ACTION_TYPES, name="admin_action_type")
    admin_action_enum.drop(op.get_bind(), checkfirst=True)
