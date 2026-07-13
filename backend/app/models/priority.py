import uuid
import enum
from datetime import datetime

from sqlalchemy import String, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PriorityTrack(str, enum.Enum):
    TECHNICAL = "TECHNICAL"
    LANGUAGE = "LANGUAGE"


class PriorityStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CUT = "CUT"
    REJECTED = "REJECTED"


class Priority(Base):
    __tablename__ = "priorities"
    # Partial unique index (user_id, track) WHERE status = 'ACTIVE'
    # is added via Alembic migration — SQLAlchemy UniqueConstraint
    # can't express partial indexes, and the service layer enforces
    # the cap at runtime.

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    track: Mapped[PriorityTrack] = mapped_column(Enum(PriorityTrack))
    status: Mapped[PriorityStatus] = mapped_column(
        Enum(PriorityStatus), default=PriorityStatus.ACTIVE
    )
    definition_of_done: Mapped[str] = mapped_column(Text)
    quarter_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("quarters.id"))
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
