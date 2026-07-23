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
    """Create or sync the default tracks for a user; idempotent by slug.

    Re-running this (e.g. after DEFAULT_TRACKS content changes) updates
    existing routines/items to match the latest spec instead of no-op'ing —
    matched by routine name / item title within the track. Item status and
    completed_at are never touched, so re-syncing never loses progress.
    """
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
        else:
            track.name = spec["name"]
            track.description = spec["description"]

        existing_items = (
            (await db.execute(
                select(CurriculumItem).where(CurriculumItem.track_id == track.id)
            )).scalars().all()
        )
        items_by_title = {i.title: i for i in existing_items}

        order = 0
        for section in spec["sections"]:
            for item in section["items"]:
                existing = items_by_title.get(item["title"])
                if existing:
                    existing.section = section["section"]
                    existing.details = item["details"]
                    existing.learning_goal = item.get("learning_goal")
                    existing.key_topics = item.get("key_topics")
                    existing.sort_order = order
                else:
                    db.add(
                        CurriculumItem(
                            track_id=track.id,
                            section=section["section"],
                            title=item["title"],
                            details=item["details"],
                            learning_goal=item.get("learning_goal"),
                            key_topics=item.get("key_topics"),
                            sort_order=order,
                        )
                    )
                order += 1

        existing_routines = (
            (await db.execute(
                select(PracticeRoutine).where(PracticeRoutine.track_id == track.id)
            )).scalars().all()
        )
        routines_by_name = {r.name: r for r in existing_routines}

        for i, routine in enumerate(spec["routines"]):
            existing = routines_by_name.get(routine["name"])
            if existing:
                existing.minutes = routine["minutes"]
                existing.rest_weekdays = routine["rest_weekdays"]
                existing.sort_order = i
            else:
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
