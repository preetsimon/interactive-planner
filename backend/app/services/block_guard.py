"""Block Guard — flags violations on time_blocks insert, never rejects."""
from typing import Optional
import uuid
from datetime import datetime, time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.time_block import TimeBlock
from app.models.protected_window import ProtectedWindow
from app.models.user import User


async def check_protected_window(
    db: AsyncSession, block: TimeBlock
) -> tuple[bool, Optional[uuid.UUID]]:
    """Check if a block overlaps any active protected window. Returns (violation, window_id)."""
    weekday = block.start_at.isoweekday()
    result = await db.execute(
        select(ProtectedWindow).where(
            ProtectedWindow.user_id == block.user_id,
            ProtectedWindow.active == True,  # noqa: E712
        )
    )
    for pw in result.scalars().all():
        if pw.days_of_week and weekday not in pw.days_of_week:
            continue
        # Check time overlap
        block_start_time = block.start_at.time()
        block_end_time = block.end_at.time()
        if block_start_time < pw.end_time and block_end_time > pw.start_time:
            # Check if category is NOT in allowed list
            if pw.allowed_category_ids and str(block.category_id) not in [
                str(c) for c in pw.allowed_category_ids
            ]:
                return True, pw.id
    return False, None


async def check_cutoff(db: AsyncSession, block: TimeBlock) -> bool:
    """Check if block violates work cutoff time."""
    user_result = await db.execute(
        select(User).where(User.id == block.user_id)
    )
    user = user_result.scalar_one_or_none()
    if not user or not user.work_cutoff_time:
        return False
    block_end_time = block.end_at.time()
    return block_end_time > user.work_cutoff_time


async def apply_block_guard(db: AsyncSession, block: TimeBlock) -> TimeBlock:
    """Apply block guard checks to a time block (flags, never rejects)."""
    violation, window_id = await check_protected_window(db, block)
    block.violates_protected_window = violation

    cutoff_violation = await check_cutoff(db, block)
    block.violates_cutoff = cutoff_violation

    await db.commit()
    await db.refresh(block)
    return block
