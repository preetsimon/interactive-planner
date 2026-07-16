from typing import Optional
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Time, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProtectedWindow(Base):
    __tablename__ = "protected_windows"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    start_time: Mapped[datetime] = mapped_column(Time)
    end_time: Mapped[datetime] = mapped_column(Time)
    days_of_week: Mapped[Optional[list[int]]] = mapped_column(JSON)
    allowed_category_ids: Mapped[Optional[list[str]]] = mapped_column(JSON)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
