"""add admin api layer

Revision ID: c360a4647395
Revises: 1bc6a909a2da
Create Date: 2025-10-17 01:27:50.953913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c360a4647395"
down_revision: Union[str, None] = "1bc6a909a2da"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    admin_level_enum = sa.Enum("NONE", "ADMIN_LEVEL_1", "ADMIN_LEVEL_2", "ADMIN_LEVEL_3", name="admin_level")
    admin_level_enum.create(op.get_bind(), checkfirst=True)

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_columns = {col["name"] for col in inspector.get_columns("users")}

    if "admin_level" not in existing_columns:
        op.add_column(
            "users",
            sa.Column("admin_level", admin_level_enum, nullable=False, server_default="none"),
        )
        if bind.dialect.name != "sqlite":
            op.alter_column("users", "admin_level", server_default=None)

    if "permissions" not in existing_columns:
        op.add_column("users", sa.Column("permissions", sa.JSON(), nullable=True))

    if "admin_logs" not in inspector.get_table_names():
        op.create_table(
            "admin_logs",
            sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
            sa.Column("admin_id", sa.String(length=36), nullable=True),
            sa.Column("action", sa.String(length=120), nullable=False),
            sa.Column("target_id", sa.String(length=120), nullable=True),
            sa.Column("details", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        )
        op.create_index("ix_admin_logs_admin_id", "admin_logs", ["admin_id"])


def downgrade() -> None:
    op.drop_index("ix_admin_logs_admin_id", table_name="admin_logs")
    op.drop_table("admin_logs")

    op.drop_column("users", "permissions")
    op.drop_column("users", "admin_level")

    admin_level_enum = sa.Enum("NONE", "ADMIN_LEVEL_1", "ADMIN_LEVEL_2", "ADMIN_LEVEL_3", name="admin_level")
    admin_level_enum.drop(op.get_bind(), checkfirst=True)
