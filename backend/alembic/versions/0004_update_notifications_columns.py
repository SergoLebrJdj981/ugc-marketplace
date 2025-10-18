"""Update notifications table structure."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_update_notifications_columns"
down_revision: Union[str, Sequence[str], None] = "0003_add_messages_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("notifications") as batch:
        batch.add_column(sa.Column("title", sa.String(length=160), nullable=False, server_default=""))
        batch.add_column(sa.Column("content", sa.String(length=1024), nullable=False, server_default=""))
        batch.add_column(sa.Column("related_id", sa.String(length=120), nullable=True))
        batch.alter_column("is_read", server_default=sa.text("0"), existing_type=sa.Boolean(), nullable=False)
        batch.drop_column("message")

    op.execute("UPDATE notifications SET title = 'Уведомление' WHERE title = ''")

    with op.batch_alter_table("notifications") as batch:
        batch.alter_column("title", server_default=None)
        batch.alter_column("content", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("notifications") as batch:
        batch.add_column(sa.Column("message", sa.String(length=255), nullable=False, server_default=""))
        batch.drop_column("related_id")
        batch.drop_column("content")
        batch.drop_column("title")
        batch.alter_column("is_read", server_default=None, existing_type=sa.Boolean(), nullable=True)

    op.execute("UPDATE notifications SET message = title WHERE message = ''")

    with op.batch_alter_table("notifications") as batch:
        batch.alter_column("message", server_default=None)
