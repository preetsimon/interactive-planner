import uuid
import enum
from datetime import date, datetime, timezone

from sqlalchemy import String, Enum, ForeignKey, Date, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DeadlineStatus(str, enum.Enum):
    OPEN = "OPEN"
    SHIPPED_COMPLETE = "SHIPPED_COMPLETE"
    SHIPPED_PARTIAL = "SHIPPED_PARTIAL"


class Deadline(Base):
    __tablename__ = "deadlines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    priority_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("priorities.id"))
    due_date: Mapped[date] = mapped_column(Date)
    status: Mapped[DeadlineStatus] = mapped_column(
        Enum(DeadlineStatus), default=DeadlineStatus.OPEN
    )
    scope_cuts: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
