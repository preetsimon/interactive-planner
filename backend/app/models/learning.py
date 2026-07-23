from typing import Optional
import uuid
import enum
from datetime import datetime, date

from sqlalchemy import Boolean, String, Enum, ForeignKey, Text, Integer, Date, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ItemStatus(str, enum.Enum):
    PENDING = "PENDING"
    DONE = "DONE"


class LearningTrack(Base):
    __tablename__ = "learning_tracks"
    __table_args__ = (UniqueConstraint("user_id", "slug"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    slug: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )


class CurriculumItem(Base):
    __tablename__ = "curriculum_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    track_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learning_tracks.id"))
    section: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(255))
    details: Mapped[Optional[str]] = mapped_column(Text)
    # What you're trying to accomplish with this item — surfaced as the
    # synced block's first action in Ignition.
    learning_goal: Mapped[Optional[str]] = mapped_column(Text)
    # Concrete topics/concepts covered — "by the end you'll know X, Y, Z".
    key_topics: Mapped[Optional[list[str]]] = mapped_column(JSON)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[ItemStatus] = mapped_column(
        Enum(ItemStatus), default=ItemStatus.PENDING
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(default=None)


class PracticeRoutine(Base):
    __tablename__ = "practice_routines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    track_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learning_tracks.id"))
    name: Mapped[str] = mapped_column(String(255))
    minutes: Mapped[Optional[int]] = mapped_column(Integer)
    # Weekday numbers (Mon=0 .. Sun=6) on which this routine is not scheduled;
    # rest days neither extend nor break the streak.
    rest_weekdays: Mapped[Optional[list[int]]] = mapped_column(JSON)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class PracticeLog(Base):
    __tablename__ = "practice_logs"
    __table_args__ = (UniqueConstraint("routine_id", "log_date"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    routine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("practice_routines.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    log_date: Mapped[date] = mapped_column(Date)
    minutes: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow()
    )


class BlockFeedback(Base):
    __tablename__ = "block_feedback"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    log_date: Mapped[date] = mapped_column(Date)
    block_title: Mapped[str] = mapped_column(String(255))
    track_slug: Mapped[Optional[str]] = mapped_column(String(64))
    curriculum_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("curriculum_items.id")
    )
    routine_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("practice_routines.id")
    )
    status: Mapped[str] = mapped_column(String(16))
    planned_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    actual_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    confidence: Mapped[Optional[int]] = mapped_column(Integer)
    difficulty: Mapped[Optional[int]] = mapped_column(Integer)
    what_worked: Mapped[Optional[str]] = mapped_column(Text)
    needs_practice: Mapped[Optional[str]] = mapped_column(Text)
    repeat_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow()
    )
