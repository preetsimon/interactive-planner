"""Machine-to-machine endpoints consumed by Ignition.

Auth: X-Service-Key header (shared secret), not JWT — Ignition is a
single-user local service, not a browser session.
"""
from typing import Optional
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.api.deps import verify_service_key
from app.models.learning import (
    LearningTrack,
    CurriculumItem,
    PracticeRoutine,
    PracticeLog,
    ItemStatus,
)
from app.models.priority import Priority, PriorityStatus
from app.models.quarter import Quarter
from app.services.cadence import get_current_quarter, tick

router = APIRouter(
    prefix="/integration",
    tags=["integration"],
    dependencies=[Depends(verify_service_key)],
)


# ---------- GET /weekly-plan ----------

class SuggestedBlock(BaseModel):
    day_offset: int
    title: str
    first_action: str
    minutes: int
    track: str
    curriculum_item_id: Optional[str] = None
    routine_id: Optional[str] = None


class ActivePriority(BaseModel):
    track: str
    title: str


class WeeklyPlanResponse(BaseModel):
    week_start: str
    phase: Optional[str]
    priorities: list[ActivePriority]
    suggested_blocks: list[SuggestedBlock]


@router.get("/weekly-plan", response_model=WeeklyPlanResponse)
async def weekly_plan(
    week_start: Optional[str] = None,
    user_email: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    ws = date.fromisoformat(week_start) if week_start else _next_monday()

    user = await _resolve_user(db, user_email)
    user_id = user.id if user else None

    phase = None
    priorities: list[ActivePriority] = []
    blocks: list[SuggestedBlock] = []

    if user_id:
        quarter = await tick(db, user_id)
        if quarter:
            phase = quarter.phase.value

        result = await db.execute(
            select(Priority).where(
                Priority.user_id == user_id,
                Priority.status == PriorityStatus.ACTIVE,
            )
        )
        priorities = [
            ActivePriority(track=p.track.value, title=p.title)
            for p in result.scalars().all()
        ]

        blocks = await _generate_suggested_blocks(db, user_id, ws, phase)

    return WeeklyPlanResponse(
        week_start=ws.isoformat(),
        phase=phase,
        priorities=priorities,
        suggested_blocks=blocks,
    )


async def _generate_suggested_blocks(
    db: AsyncSession,
    user_id,
    week_start: date,
    phase: Optional[str],
) -> list[SuggestedBlock]:
    result = await db.execute(
        select(LearningTrack).where(LearningTrack.user_id == user_id)
    )
    tracks = result.scalars().all()

    blocks: list[SuggestedBlock] = []

    for track in tracks:
        routines_result = await db.execute(
            select(PracticeRoutine)
            .where(PracticeRoutine.track_id == track.id)
            .order_by(PracticeRoutine.sort_order)
        )
        routines = routines_result.scalars().all()

        next_items = await _next_pending_items(db, track.id, limit=7)
        item_cursor = 0

        is_rest_phase = phase == "REST"

        for routine in routines:
            rest_days = set(routine.rest_weekdays or [])

            if is_rest_phase and routine.sort_order > 0:
                continue

            for day_offset in range(7):
                day = week_start + timedelta(days=day_offset)
                weekday = day.weekday()

                if weekday in rest_days:
                    continue

                curriculum_item = None
                if item_cursor < len(next_items):
                    curriculum_item = next_items[item_cursor]

                title = _block_title(track.slug, routine.name, curriculum_item)
                first_action = _block_first_action(routine.name, curriculum_item)

                blocks.append(SuggestedBlock(
                    day_offset=day_offset,
                    title=title,
                    first_action=first_action,
                    minutes=routine.minutes or 60,
                    track=track.slug,
                    curriculum_item_id=str(curriculum_item.id) if curriculum_item else None,
                    routine_id=str(routine.id),
                ))

                if curriculum_item and routine.sort_order == 0:
                    item_cursor += 1

    return blocks


async def _next_pending_items(db: AsyncSession, track_id, limit: int = 7):
    result = await db.execute(
        select(CurriculumItem)
        .where(
            CurriculumItem.track_id == track_id,
            CurriculumItem.status == ItemStatus.PENDING,
        )
        .order_by(CurriculumItem.sort_order)
        .limit(limit)
    )
    return result.scalars().all()


def _block_title(slug: str, routine_name: str, item: Optional[CurriculumItem]) -> str:
    prefix = "Py" if "python" in slug else "Fr" if "french" in slug else slug[:8]
    if item:
        return f"{prefix}: {item.title}"
    return f"{prefix}: {routine_name}"


def _block_first_action(routine_name: str, item: Optional[CurriculumItem]) -> str:
    if item and item.details:
        first_sentence = item.details.split(". ")[0]
        return first_sentence[:120] if len(first_sentence) > 120 else first_sentence
    return f"Open materials for: {routine_name}"


# ---------- POST /day-results ----------

class BlockResult(BaseModel):
    title: str
    status: str
    planned_minutes: Optional[int] = None
    actual_minutes: Optional[float] = None
    curriculum_item_id: Optional[str] = None
    routine_id: Optional[str] = None


class DayResultsRequest(BaseModel):
    date: str
    blocks: list[BlockResult]


class DayResultsResponse(BaseModel):
    items_marked_done: int
    practice_logs_written: int


@router.post("/day-results", response_model=DayResultsResponse)
async def day_results(
    payload: DayResultsRequest,
    user_email: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await _resolve_user(db, user_email)
    if not user:
        return DayResultsResponse(items_marked_done=0, practice_logs_written=0)

    log_date = date.fromisoformat(payload.date)
    items_done = 0
    logs_written = 0

    for block in payload.blocks:
        if block.status not in ("done", "partial"):
            continue

        if block.curriculum_item_id and block.status == "done":
            from uuid import UUID
            result = await db.execute(
                select(CurriculumItem)
                .join(LearningTrack, CurriculumItem.track_id == LearningTrack.id)
                .where(
                    CurriculumItem.id == UUID(block.curriculum_item_id),
                    LearningTrack.user_id == user.id,
                )
            )
            item = result.scalar_one_or_none()
            if item and item.status != ItemStatus.DONE:
                from datetime import datetime
                item.status = ItemStatus.DONE
                item.completed_at = datetime.utcnow()
                items_done += 1

        if block.routine_id:
            from uuid import UUID
            routine_uuid = UUID(block.routine_id)
            existing = await db.execute(
                select(PracticeLog).where(
                    PracticeLog.routine_id == routine_uuid,
                    PracticeLog.log_date == log_date,
                )
            )
            log = existing.scalar_one_or_none()
            minutes = int(block.actual_minutes) if block.actual_minutes else (block.planned_minutes or 0)
            if log:
                log.minutes = minutes
            else:
                db.add(PracticeLog(
                    routine_id=routine_uuid,
                    user_id=user.id,
                    log_date=log_date,
                    minutes=minutes,
                ))
            logs_written += 1

    await db.commit()
    return DayResultsResponse(items_marked_done=items_done, practice_logs_written=logs_written)


# ---------- helpers ----------

async def _resolve_user(db: AsyncSession, email: Optional[str]):
    from app.models.user import User
    if email:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    result = await db.execute(select(User).order_by(User.created_at).limit(1))
    return result.scalar_one_or_none()


def _next_monday() -> date:
    today = date.today()
    days_ahead = (7 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)
