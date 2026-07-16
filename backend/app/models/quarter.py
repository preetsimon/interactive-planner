from typing import Optional
import uuid
import enum
from datetime import date, datetime, timezone

from sqlalchemy import String, Enum, Integer, Date, Text, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Phase(str, enum.Enum):
    REST = "REST"
    REVIEW = "REVIEW"
    SPRINT = "SPRINT"
    CLOSED = "CLOSED"


class Quarter(Base):
    __tablename__ = "quarters"
    __table_args__ = (
        UniqueConstraint("user_id", "year", "quarter_num", name="uq_quarter_per_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    year: Mapped[int] = mapped_column(Integer)
    quarter_num: Mapped[int] = mapped_column(Integer)
    theme: Mapped[str] = mapped_column(Text, default="")
    phase: Mapped[Phase] = mapped_column(Enum(Phase), default=Phase.REST)
    rest_start: Mapped[Optional[date]] = mapped_column(Date)
    review_start: Mapped[Optional[date]] = mapped_column(Date)
    sprint_start: Mapped[Optional[date]] = mapped_column(Date)
    sprint_end: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
