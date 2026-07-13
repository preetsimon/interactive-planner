"""Identity Audit — weekly comparison of logged hours vs stated goals."""
import uuid
from datetime import date, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.time_block import TimeBlock
from app.models.category import Category
from app.models.user import User


async def run_identity_audit(
    db: AsyncSession, user_id: uuid.UUID, week_start: date
) -> dict:
    week_end = week_start + timedelta(days=7)

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one()
    threshold = user.weekly_goal_hours_threshold

    result = await db.execute(
        select(
            Category.name,
            Category.goal_aligned,
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
        .group_by(Category.name, Category.goal_aligned)
    )

    rows = result.all()
    goal_hours = sum(float(r.hours or 0) for r in rows if r.goal_aligned)
    total_hours = sum(float(r.hours or 0) for r in rows)

    if total_hours == 0:
        return {
            "verdict": "MISALIGNED",
            "reason": "NO_DATA",
            "goal_hours": 0,
            "threshold": threshold,
            "category_breakdown": [],
        }

    return {
        "verdict": "ALIGNED" if goal_hours >= threshold else "MISALIGNED",
        "goal_hours": goal_hours,
        "threshold": threshold,
        "total_hours": total_hours,
        "category_breakdown": [
            {"name": r.name, "hours": float(r.hours or 0), "goal_aligned": r.goal_aligned}
            for r in rows
        ],
    }
