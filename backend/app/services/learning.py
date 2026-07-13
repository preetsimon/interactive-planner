"""Learning tracks: default-curriculum seeding and practice-streak math."""

import uuid
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learning import (
    LearningTrack,
    CurriculumItem,
    PracticeRoutine,
)
from app.services.learning_curricula import DEFAULT_TRACKS


async def seed_default_tracks(
    db: AsyncSession, user_id: uuid.UUID
) -> list[LearningTrack]:
    """Create the default tracks for a user; idempotent by slug."""
    tracks: list[LearningTrack] = []
    for spec in DEFAULT_TRACKS:
        result = await db.execute(
            select(LearningTrack).where(
                LearningTrack.user_id == user_id,
                LearningTrack.slug == spec["slug"],
            )
        )
        track = result.scalar_one_or_none()
        if track is None:
            track = LearningTrack(
                user_id=user_id,
                slug=spec["slug"],
                name=spec["name"],
                description=spec["description"],
            )
            db.add(track)
            await db.flush()
            order = 0
            for section in spec["sections"]:
                for item in section["items"]:
                    db.add(
                        CurriculumItem(
                            track_id=track.id,
                            section=section["section"],
                            title=item["title"],
                            details=item["details"],
                            sort_order=order,
                        )
                    )
                    order += 1
            for i, routine in enumerate(spec["routines"]):
                db.add(
                    PracticeRoutine(
                        track_id=track.id,
                        name=routine["name"],
                        minutes=routine["minutes"],
                        rest_weekdays=routine["rest_weekdays"],
                        sort_order=i,
                    )
                )
        tracks.append(track)
    await db.commit()
    return tracks


def compute_streak(
    logged: set[date], rest_weekdays: set[int], today: date
) -> int:
    """Consecutive logged days ending at today.

    Rest days neither extend nor break the streak (but a log on a rest day
    still counts). Today being unlogged doesn't break the streak — the day
    isn't over yet — so counting starts from yesterday in that case.
    """
    day = today
    if day not in logged:
        day -= timedelta(days=1)
    streak = 0
    while True:
        if day in logged:
            streak += 1
        elif day.weekday() not in rest_weekdays:
            break
        day -= timedelta(days=1)
    return streak
