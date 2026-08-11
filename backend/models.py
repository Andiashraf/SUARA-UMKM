from datetime import datetime, timezone
import uuid

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class FanWallMessageModel(Base):
    __tablename__ = "fan_wall_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    business_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    province: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    city_regency: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    avatar_url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    likes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("ix_fan_wall_approved_created", "is_approved", "created_at"),
        Index("ix_fan_wall_approved_likes", "is_approved", "likes_count"),
    )


class FanWallReactionModel(Base):
    __tablename__ = "fan_wall_reactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    voter_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (UniqueConstraint("message_id", "voter_hash", name="uq_message_voter"),)