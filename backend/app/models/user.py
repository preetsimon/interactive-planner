from typing import Optional
import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text)
    stated_goal: Mapped[Optional[str]] = mapped_column(Text)
    work_cutoff_time: Mapped[Optional[datetime]] = mapped_column(Time)
    weekly_goal_hours_threshold: Mapped[int] = mapped_column(Integer, default=10)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
