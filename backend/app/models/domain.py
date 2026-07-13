import uuid
import enum
from datetime import datetime

from sqlalchemy import String, Numeric, Enum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DomainStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CUT = "CUT"


class TargetDomain(Base):
    __tablename__ = "target_domains"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))
    required_assets: Mapped[list[str] | None] = mapped_column(JSON)
    score: Mapped[float] = mapped_column(Numeric(3, 2), default=0)
    status: Mapped[DomainStatus] = mapped_column(
        Enum(DomainStatus), default=DomainStatus.ACTIVE
    )
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
