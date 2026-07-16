from typing import Optional
import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, CheckConstraint, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TimeBlock(Base):
    __tablename__ = "time_blocks"
    __table_args__ = (
        CheckConstraint("end_at > start_at", name="ck_time_blocks_end_after_start"),
        Index("ix_time_blocks_user_start", "user_id", "start_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"))
    start_at: Mapped[datetime] = mapped_column()
    end_at: Mapped[datetime] = mapped_column()
    notes: Mapped[Optional[str]] = mapped_column(Text)
    violates_protected_window: Mapped[bool] = mapped_column(Boolean, default=False)
    violates_cutoff: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
