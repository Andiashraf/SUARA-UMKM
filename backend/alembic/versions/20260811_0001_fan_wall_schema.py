"""Create Fan Wall schema

Revision ID: 20260811_0001
Revises:
Create Date: 2026-08-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260811_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fan_wall_messages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("full_name", sa.String(length=80), nullable=False),
        sa.Column("business_name", sa.String(length=120), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("province", sa.String(length=50), nullable=False),
        sa.Column("city_regency", sa.String(length=80), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("avatar_url", sa.Text(), nullable=False),
        sa.Column("likes_count", sa.Integer(), nullable=False),
        sa.Column("is_approved", sa.Boolean(), nullable=False),
        sa.Column("is_featured", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fan_wall_messages_full_name", "fan_wall_messages", ["full_name"])
    op.create_index("ix_fan_wall_messages_business_name", "fan_wall_messages", ["business_name"])
    op.create_index("ix_fan_wall_messages_role", "fan_wall_messages", ["role"])
    op.create_index("ix_fan_wall_messages_province", "fan_wall_messages", ["province"])
    op.create_index("ix_fan_wall_messages_is_approved", "fan_wall_messages", ["is_approved"])
    op.create_index("ix_fan_wall_approved_created", "fan_wall_messages", ["is_approved", "created_at"])
    op.create_index("ix_fan_wall_approved_likes", "fan_wall_messages", ["is_approved", "likes_count"])
    op.create_table(
        "fan_wall_reactions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("message_id", sa.String(length=36), nullable=False),
        sa.Column("voter_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("message_id", "voter_hash", name="uq_message_voter"),
    )
    op.create_index("ix_fan_wall_reactions_message_id", "fan_wall_reactions", ["message_id"])


def downgrade() -> None:
    op.drop_index("ix_fan_wall_reactions_message_id", table_name="fan_wall_reactions")
    op.drop_table("fan_wall_reactions")
    op.drop_index("ix_fan_wall_approved_likes", table_name="fan_wall_messages")
    op.drop_index("ix_fan_wall_approved_created", table_name="fan_wall_messages")
    op.drop_index("ix_fan_wall_messages_is_approved", table_name="fan_wall_messages")
    op.drop_index("ix_fan_wall_messages_province", table_name="fan_wall_messages")
    op.drop_index("ix_fan_wall_messages_role", table_name="fan_wall_messages")
    op.drop_index("ix_fan_wall_messages_business_name", table_name="fan_wall_messages")
    op.drop_index("ix_fan_wall_messages_full_name", table_name="fan_wall_messages")
    op.drop_table("fan_wall_messages")