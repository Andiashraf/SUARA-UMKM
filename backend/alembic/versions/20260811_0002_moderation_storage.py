"""Add moderation and avatar storage fields

Revision ID: 20260811_0002
Revises: 20260811_0001
Create Date: 2026-08-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260811_0002"
down_revision: Union[str, Sequence[str], None] = "20260811_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("fan_wall_messages", sa.Column("avatar_path", sa.Text(), nullable=True))
    op.add_column(
        "fan_wall_messages",
        sa.Column("moderation_status", sa.String(length=12), server_default="pending", nullable=False),
    )
    op.add_column(
        "fan_wall_messages",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.execute("UPDATE fan_wall_messages SET moderation_status = CASE WHEN is_approved THEN 'approved' ELSE 'pending' END")
    op.create_check_constraint(
        "ck_fan_wall_moderation_status",
        "fan_wall_messages",
        "moderation_status IN ('pending', 'approved', 'rejected')",
    )
    op.create_index("ix_fan_wall_messages_moderation_status", "fan_wall_messages", ["moderation_status"])
    op.create_index("ix_fan_wall_status_created", "fan_wall_messages", ["moderation_status", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_fan_wall_status_created", table_name="fan_wall_messages")
    op.drop_index("ix_fan_wall_messages_moderation_status", table_name="fan_wall_messages")
    op.drop_constraint("ck_fan_wall_moderation_status", "fan_wall_messages", type_="check")
    op.drop_column("fan_wall_messages", "updated_at")
    op.drop_column("fan_wall_messages", "moderation_status")
    op.drop_column("fan_wall_messages", "avatar_path")