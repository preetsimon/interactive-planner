"""Cadence Engine — quarterly phase state machine.

CLOSED → REST → REVIEW → SPRINT → CLOSED
"""
import uuid
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quarter import Quarter, Phase


async def get_current_quarter(db: AsyncSession, user_id: uuid.UUID) -> Quarter | None:
    result = await db.execute(
        select(Quarter)
        .where(Quarter.user_id == user_id)
        .order_by(Quarter.year.desc(), Quarter.quarter_num.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create_quarter(
    db: AsyncSession, user_id: uuid.UUID, year: int, quarter_num: int, theme: str = ""
) -> Quarter:
    # Calculate dates based on quarter
    quarter_start = date(year, (quarter_num - 1) * 3 + 1, 1)
    rest_end = quarter_start + timedelta(days=7)
    review_end = rest_end + timedelta(days=7)
    sprint_start = review_end
    sprint_end = sprint_start + timedelta(weeks=8)

    quarter = Quarter(
        user_id=user_id,
        year=year,
        quarter_num=quarter_num,
        theme=theme,
        phase=Phase.REST,
        rest_start=quarter_start,
        review_start=rest_end,
        sprint_start=sprint_start,
        sprint_end=sprint_end,
    )
    db.add(quarter)
    await db.commit()
    await db.refresh(quarter)
    return quarter


async def tick(db: AsyncSession, user_id: uuid.UUID, today: date | None = None) -> Quarter | None:
    """Advance the phase if today crosses a boundary. Idempotent."""
    if today is None:
        today = date.today()

    quarter = await get_current_quarter(db, user_id)
    if not quarter:
        return None

    # Determine what phase today belongs to
    if quarter.rest_start and today >= quarter.rest_start and today < (quarter.review_start or today):
        target_phase = Phase.REST
    elif quarter.review_start and today >= quarter.review_start and today < (quarter.sprint_start or today):
        target_phase = Phase.REVIEW
    elif quarter.sprint_start and today >= quarter.sprint_start and today <= (quarter.sprint_end or today):
        target_phase = Phase.SPRINT
    elif quarter.sprint_end and today > quarter.sprint_end:
        target_phase = Phase.CLOSED
    else:
        return quarter

    if quarter.phase != target_phase:
        quarter.phase = target_phase
        await db.commit()
        await db.refresh(quarter)

    return quarter
