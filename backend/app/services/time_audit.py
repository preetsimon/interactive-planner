"""Time Audit — weekly proactive/reactive ratio."""
import uuid
from datetime import date, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.time_block import TimeBlock
from app.models.category import Category, Classification


async def run_time_audit(
    db: AsyncSession, user_id: uuid.UUID, week_start: date
) -> dict:
    week_end = week_start + timedelta(days=7)

    result = await db.execute(
        select(
            Category.classification,
            func.sum(
                func.extract("epoch", TimeBlock.end_at - TimeBlock.start_at) / 3600
            ).label("hours"),
        )
        .join(TimeBlock, TimeBlock.category_id == Category.id)
        .where(
            TimeBlock.user_id == user_id,
            TimeBlock.start_at >= week_start.isoformat(),
            TimeBlock.start_at < week_end.isoformat(),
        )
        .group_by(Category.classification)
    )

    breakdown = {row.classification: float(row.hours or 0) for row in result.all()}

    proactive = breakdown.get(Classification.PROACTIVE, 0)
    reactive = breakdown.get(Classification.REACTIVE, 0)
    ratio = proactive / max(reactive, 0.001)

    return {
        "proactive_hours": proactive,
        "reactive_hours": reactive,
        "ratio": round(ratio, 2),
        "verdict": "ALIGNED" if ratio >= 1.0 else "REACTIVE_DOMINANT",
        "category_breakdown": breakdown,
    }
