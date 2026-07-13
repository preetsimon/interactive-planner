"""Priority Gate — hard cap: 1 active TECHNICAL + 1 active LANGUAGE.

Second active → HTTP 409. Cutting is a first-class success action.
"""
import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.priority import Priority, PriorityTrack, PriorityStatus
from app.schemas.priority import PriorityCreate


async def get_active_count(db: AsyncSession, user_id: uuid.UUID, track: PriorityTrack) -> int:
    result = await db.execute(
        select(func.count()).where(
            Priority.user_id == user_id,
            Priority.track == track,
            Priority.status == PriorityStatus.ACTIVE,
        )
    )
    return result.scalar_one()


async def add_priority(db: AsyncSession, user_id: uuid.UUID, payload: PriorityCreate) -> Priority:
    count = await get_active_count(db, user_id, payload.track)
    if count >= 1:
        # Find the blocking priority for the error response
        blocking = await db.execute(
            select(Priority).where(
                Priority.user_id == user_id,
                Priority.track == payload.track,
                Priority.status == PriorityStatus.ACTIVE,
            )
        )
        bp = blocking.scalar_one()
        raise PriorityCapError(bp)

    priority = Priority(
        user_id=user_id,
        title=payload.title,
        track=payload.track,
        definition_of_done=payload.definition_of_done,
        status=PriorityStatus.ACTIVE,
    )
    db.add(priority)
    await db.commit()
    await db.refresh(priority)
    return priority


async def cut_priority(db: AsyncSession, priority_id: uuid.UUID) -> Priority:
    result = await db.execute(
        select(Priority).where(Priority.id == priority_id)
    )
    priority = result.scalar_one()
    priority.status = PriorityStatus.CUT
    await db.commit()
    await db.refresh(priority)
    return priority


async def complete_priority(db: AsyncSession, priority_id: uuid.UUID) -> Priority:
    result = await db.execute(
        select(Priority).where(Priority.id == priority_id)
    )
    priority = result.scalar_one()
    priority.status = PriorityStatus.COMPLETED
    await db.commit()
    await db.refresh(priority)
    return priority


class PriorityCapError(Exception):
    def __init__(self, blocking_priority: Priority):
        self.blocking_priority = blocking_priority
        super().__init__("PRIORITY_CAP")
