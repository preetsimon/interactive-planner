import uuid
import enum
from datetime import datetime

from sqlalchemy import String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Classification(str, enum.Enum):
    PROACTIVE = "PROACTIVE"
    REACTIVE = "REACTIVE"
    NEUTRAL = "NEUTRAL"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    classification: Mapped[Classification] = mapped_column(Enum(Classification))
    goal_aligned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
