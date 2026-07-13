"""Deadline Enforcer — at due_date, force ship if not completed. Never extend."""
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deadline import Deadline, DeadlineStatus
from app.models.priority import Priority, PriorityStatus


async def enforce(db: AsyncSession, deadline_id: uuid.UUID) -> Deadline:
    result = await db.execute(select(Deadline).where(Deadline.id == deadline_id))
    deadline = result.scalar_one()

    # Get the priority
    priority_result = await db.execute(
        select(Priority).where(Priority.id == deadline.priority_id)
    )
    priority = priority_result.scalar_one()

    if priority.status != PriorityStatus.COMPLETED:
        # Force ship
        deadline.status = DeadlineStatus.SHIPPED_PARTIAL
        priority.status = PriorityStatus.COMPLETED
        await db.commit()
        await db.refresh(deadline)

    return deadline
