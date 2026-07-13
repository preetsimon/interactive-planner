import uuid
import enum
from datetime import date, datetime, timezone

from sqlalchemy import String, Enum, ForeignKey, Date, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditType(str, enum.Enum):
    TIME_AUDIT = "TIME_AUDIT"
    IDENTITY_AUDIT = "IDENTITY_AUDIT"
    MONTHLY_CHECKPOINT = "MONTHLY_CHECKPOINT"
    QUARTERLY_REVIEW = "QUARTERLY_REVIEW"


class Verdict(str, enum.Enum):
    ALIGNED = "ALIGNED"
    MISALIGNED = "MISALIGNED"
    ON_TRACK = "ON_TRACK"
    BEHIND = "BEHIND"


class AuditReport(Base):
    __tablename__ = "audit_reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    type: Mapped[AuditType] = mapped_column(Enum(AuditType))
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    payload: Mapped[dict | None] = mapped_column(JSON)
    verdict: Mapped[Verdict] = mapped_column(Enum(Verdict))
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )


class AuditLogEntry(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    event_type: Mapped[str] = mapped_column(String(50))
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[uuid.UUID | None] = mapped_column()
    detail: Mapped[dict | None] = mapped_column(JSON)
    occurred_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow()
    )
