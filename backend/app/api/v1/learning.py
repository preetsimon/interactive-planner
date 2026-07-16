from typing import Optional
import uuid
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.learning import (
    LearningTrack,
    CurriculumItem,
    PracticeRoutine,
    PracticeLog,
    ItemStatus,
)
from app.schemas.learning import (
    TrackRead,
    TrackDetailRead,
    CurriculumItemRead,
    PracticeLogCreate,
    PracticeLogRead,
)
from app.services.learning import seed_default_tracks, compute_streak

router = APIRouter(prefix="/learning", tags=["learning"])


async def _progress_by_track(
    db: AsyncSession, track_ids: list[uuid.UUID]
) -> dict[uuid.UUID, tuple[int, int]]:
    if not track_ids:
        return {}
    result = await db.execute(
        select(
            CurriculumItem.track_id,
            func.count(),
            func.sum(case((CurriculumItem.status == ItemStatus.DONE, 1), else_=0)),
        )
        .where(CurriculumItem.track_id.in_(track_ids))
        .group_by(CurriculumItem.track_id)
    )
    return {track_id: (total, int(done or 0)) for track_id, total, done in result.all()}


def _track_dict(track: LearningTrack, total: int, done: int) -> dict:
    return {
        "id": track.id,
        "slug": track.slug,
        "name": track.name,
        "description": track.description,
        "items_total": total,
        "items_done": done,
    }


@router.post("/seed-defaults", response_model=list[TrackRead])
async def seed_defaults(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tracks = await seed_default_tracks(db, user.id)
    progress = await _progress_by_track(db, [t.id for t in tracks])
    return [_track_dict(t, *progress.get(t.id, (0, 0))) for t in tracks]


@router.get("/tracks", response_model=list[TrackRead])
async def list_tracks(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(LearningTrack)
        .where(LearningTrack.user_id == user.id)
        .order_by(LearningTrack.created_at)
    )
    tracks = result.scalars().all()
    progress = await _progress_by_track(db, [t.id for t in tracks])
    return [_track_dict(t, *progress.get(t.id, (0, 0))) for t in tracks]


@router.get("/tracks/{track_id}", response_model=TrackDetailRead)
async def get_track(
    track_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    track = await _get_owned_track(db, track_id, user)

    items_result = await db.execute(
        select(CurriculumItem)
        .where(CurriculumItem.track_id == track.id)
        .order_by(CurriculumItem.sort_order)
    )
    items = items_result.scalars().all()

    routines_result = await db.execute(
        select(PracticeRoutine)
        .where(PracticeRoutine.track_id == track.id)
        .order_by(PracticeRoutine.sort_order)
    )
    routines = routines_result.scalars().all()

    today = date.today()
    logs_by_routine: dict[uuid.UUID, dict[date, Optional[int]]] = {}
    if routines:
        logs_result = await db.execute(
            select(PracticeLog.routine_id, PracticeLog.log_date, PracticeLog.minutes)
            .where(PracticeLog.routine_id.in_([r.id for r in routines]))
        )
        for routine_id, log_date, minutes in logs_result.all():
            logs_by_routine.setdefault(routine_id, {})[log_date] = minutes

    routine_dicts = []
    for r in routines:
        logs = logs_by_routine.get(r.id, {})
        rest = set(r.rest_weekdays or [])
        routine_dicts.append({
            "id": r.id,
            "name": r.name,
            "minutes": r.minutes,
            "rest_weekdays": sorted(rest),
            "is_rest_today": today.weekday() in rest,
            "today_done": today in logs,
            "today_minutes": logs.get(today),
            "streak": compute_streak(set(logs), rest, today),
        })

    done = sum(1 for i in items if i.status == ItemStatus.DONE)
    return {
        **_track_dict(track, len(items), done),
        "items": items,
        "routines": routine_dicts,
    }


@router.post("/items/{item_id}/toggle", response_model=CurriculumItemRead)
async def toggle_item(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CurriculumItem)
        .join(LearningTrack, CurriculumItem.track_id == LearningTrack.id)
        .where(CurriculumItem.id == item_id, LearningTrack.user_id == user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Curriculum item not found")

    if item.status == ItemStatus.DONE:
        item.status = ItemStatus.PENDING
        item.completed_at = None
    else:
        item.status = ItemStatus.DONE
        item.completed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(item)
    return item


@router.post(
    "/routines/{routine_id}/log",
    response_model=PracticeLogRead,
    status_code=status.HTTP_201_CREATED,
)
async def log_practice(
    routine_id: uuid.UUID,
    payload: PracticeLogCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    routine = await _get_owned_routine(db, routine_id, user)
    log_date = payload.log_date or date.today()

    result = await db.execute(
        select(PracticeLog).where(
            PracticeLog.routine_id == routine.id,
            PracticeLog.log_date == log_date,
        )
    )
    log = result.scalar_one_or_none()
    if log:
        log.minutes = payload.minutes if payload.minutes is not None else log.minutes
    else:
        log = PracticeLog(
            routine_id=routine.id,
            user_id=user.id,
            log_date=log_date,
            minutes=payload.minutes if payload.minutes is not None else routine.minutes,
        )
        db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


@router.delete("/routines/{routine_id}/log", status_code=status.HTTP_204_NO_CONTENT)
async def unlog_practice(
    routine_id: uuid.UUID,
    log_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    routine = await _get_owned_routine(db, routine_id, user)
    target = log_date or date.today()
    result = await db.execute(
        select(PracticeLog).where(
            PracticeLog.routine_id == routine.id,
            PracticeLog.log_date == target,
        )
    )
    log = result.scalar_one_or_none()
    if log:
        await db.delete(log)
        await db.commit()


async def _get_owned_track(
    db: AsyncSession, track_id: uuid.UUID, user: User
) -> LearningTrack:
    result = await db.execute(
        select(LearningTrack).where(
            LearningTrack.id == track_id, LearningTrack.user_id == user.id
        )
    )
    track = result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=404, detail="Learning track not found")
    return track


async def _get_owned_routine(
    db: AsyncSession, routine_id: uuid.UUID, user: User
) -> PracticeRoutine:
    result = await db.execute(
        select(PracticeRoutine)
        .join(LearningTrack, PracticeRoutine.track_id == LearningTrack.id)
        .where(PracticeRoutine.id == routine_id, LearningTrack.user_id == user.id)
    )
    routine = result.scalar_one_or_none()
    if not routine:
        raise HTTPException(status_code=404, detail="Practice routine not found")
    return routine
