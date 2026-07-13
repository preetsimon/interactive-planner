import uuid
import enum
from datetime import datetime, date

from sqlalchemy import String, Enum, ForeignKey, Text, Integer, Date, JSON, UniqueConstraint
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
    details: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[ItemStatus] = mapped_column(
        Enum(ItemStatus), default=ItemStatus.PENDING
    )
    completed_at: Mapped[datetime | None] = mapped_column(default=None)


class PracticeRoutine(Base):
    __tablename__ = "practice_routines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    track_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learning_tracks.id"))
    name: Mapped[str] = mapped_column(String(255))
    minutes: Mapped[int | None] = mapped_column(Integer)
    # Weekday numbers (Mon=0 .. Sun=6) on which this routine is not scheduled;
    # rest days neither extend nor break the streak.
    rest_weekdays: Mapped[list[int] | None] = mapped_column(JSON)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class PracticeLog(Base):
    __tablename__ = "practice_logs"
    __table_args__ = (UniqueConstraint("routine_id", "log_date"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    routine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("practice_routines.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    log_date: Mapped[date] = mapped_column(Date)
    minutes: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow()
    )
