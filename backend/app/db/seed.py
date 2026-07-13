"""Seed the categories table with the fixed classification set from the spec."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

CATEGORIES = [
    ("JOB", "NEUTRAL", False),
    ("CODING_PROACTIVE", "PROACTIVE", True),
    ("CODING_REACTIVE", "REACTIVE", False),
    ("FRENCH_OUTPUT", "PROACTIVE", True),
    ("FRENCH_PASSIVE", "REACTIVE", False),
    ("JOB_SEARCH_NOISE", "REACTIVE", False),
    ("PASSIVE_CONSUMPTION", "REACTIVE", False),
    ("REST", "NEUTRAL", False),
    ("LIFE", "NEUTRAL", False),
]


async def seed_categories(db: AsyncSession) -> None:
    result = await db.execute(text("SELECT COUNT(*) FROM categories"))
    if result.scalar_one() > 0:
        return
    now = datetime.utcnow()
    for name, classification, goal_aligned in CATEGORIES:
        cat_id = str(uuid.uuid4())
        await db.execute(
            text(
                "INSERT INTO categories (id, name, classification, goal_aligned, created_at, updated_at) "
                "VALUES (:id, :name, :classification, :goal_aligned, :now, :now)"
            ),
            {
                "id": cat_id,
                "name": name,
                "classification": classification,
                "goal_aligned": goal_aligned,
                "now": now,
            },
        )
    await db.commit()
