"""Machine-to-machine endpoints consumed by Ignition.

Auth: X-Service-Key header (shared secret), not JWT — Ignition is a
single-user local service, not a browser session.
"""
from typing import Optional
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.api.deps import verify_service_key
from app.models.learning import (
    LearningTrack,
    CurriculumItem,
    PracticeRoutine,
    PracticeLog,
    BlockFeedback,
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

    track_adjustments = {}
    for track in tracks:
        track_adjustments[track.slug] = await _feedback_adjustments(
            db, user_id, track.slug
        )

    blocks: list[SuggestedBlock] = []

    for track in tracks:
        adj = track_adjustments[track.slug]
        routines_result = await db.execute(
            select(PracticeRoutine)
            .where(PracticeRoutine.track_id == track.id)
            .order_by(PracticeRoutine.sort_order)
        )
        routines = routines_result.scalars().all()

        next_items = await _next_pending_items(db, track.id, limit=7)
        review_items = await _items_needing_review(db, user_id, track.slug)
        item_cursor = 0
        review_cursor = 0

        is_rest_phase = phase == "REST"

        for routine in routines:
            rest_days = set(routine.rest_weekdays or [])

            if is_rest_phase and routine.sort_order > 0:
                continue

            adjusted_minutes = _adjusted_minutes(
                routine.minutes or 60, adj
            )

            for day_offset in range(7):
                day = week_start + timedelta(days=day_offset)
                weekday = day.weekday()

                if weekday in rest_days:
                    continue

                if review_cursor < len(review_items) and routine.sort_order == 0 and day_offset % 3 == 0:
                    rev_item = review_items[review_cursor]
                    blocks.append(SuggestedBlock(
                        day_offset=day_offset,
                        title=_block_title(track.slug, "Review", rev_item),
                        first_action=f"Review: {rev_item.title} — revisit areas marked for more practice",
                        minutes=max(30, adjusted_minutes // 2),
                        track=track.slug,
                        curriculum_item_id=str(rev_item.id),
                        routine_id=str(routine.id),
                    ))
                    review_cursor += 1

                curriculum_item = None
                if item_cursor < len(next_items):
                    curriculum_item = next_items[item_cursor]

                title = _block_title(track.slug, routine.name, curriculum_item)
                first_action = _block_first_action(routine.name, curriculum_item)

                if adj["avg_difficulty"] and adj["avg_difficulty"] > 3.5 and curriculum_item:
                    first_action = f"(hard topic — take it slow) {first_action}"

                blocks.append(SuggestedBlock(
                    day_offset=day_offset,
                    title=title,
                    first_action=first_action,
                    minutes=adjusted_minutes,
                    track=track.slug,
                    curriculum_item_id=str(curriculum_item.id) if curriculum_item else None,
                    routine_id=str(routine.id),
                ))

                if curriculum_item and routine.sort_order == 0:
                    item_cursor += 1

    return blocks


async def _feedback_adjustments(
    db: AsyncSession, user_id, track_slug: str
) -> dict:
    lookback = date.today() - timedelta(days=14)
    result = await db.execute(
        select(
            func.avg(BlockFeedback.confidence),
            func.avg(BlockFeedback.difficulty),
            func.avg(BlockFeedback.actual_minutes),
            func.avg(BlockFeedback.planned_minutes),
            func.count(),
        )
        .where(
            BlockFeedback.user_id == user_id,
            BlockFeedback.track_slug == track_slug,
            BlockFeedback.log_date >= lookback,
        )
    )
    row = result.first()
    avg_conf = row[0] if row else None
    avg_diff = row[1] if row else None
    avg_actual = row[2] if row else None
    avg_planned = row[3] if row else None
    count = row[4] if row else 0

    return {
        "avg_confidence": round(avg_conf, 1) if avg_conf else None,
        "avg_difficulty": round(avg_diff, 1) if avg_diff else None,
        "avg_actual": round(avg_actual) if avg_actual else None,
        "avg_planned": round(avg_planned) if avg_planned else None,
        "sample_count": count,
    }


def _adjusted_minutes(base: int, adj: dict) -> int:
    if adj["sample_count"] < 3:
        return base
    if adj["avg_actual"] and adj["avg_planned"]:
        ratio = adj["avg_actual"] / adj["avg_planned"]
        if ratio > 1.2:
            base = int(base * min(ratio, 1.5))
        elif ratio < 0.7:
            base = max(20, int(base * max(ratio, 0.6)))
    if adj["avg_difficulty"] and adj["avg_difficulty"] > 4.0:
        base = int(base * 1.15)
    elif adj["avg_confidence"] and adj["avg_confidence"] >= 4.5:
        base = max(20, int(base * 0.85))
    return base


async def _items_needing_review(
    db: AsyncSession, user_id, track_slug: str, limit: int = 3
):
    result = await db.execute(
        select(CurriculumItem)
        .join(LearningTrack, CurriculumItem.track_id == LearningTrack.id)
        .join(
            BlockFeedback,
            BlockFeedback.curriculum_item_id == CurriculumItem.id,
        )
        .where(
            LearningTrack.user_id == user_id,
            LearningTrack.slug == track_slug,
            BlockFeedback.repeat_requested == True,
        )
        .order_by(desc(BlockFeedback.log_date))
        .limit(limit)
    )
    return result.scalars().all()


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
    if item and item.learning_goal:
        return item.learning_goal[:160]
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
    confidence: Optional[int] = None
    difficulty: Optional[int] = None
    what_worked: Optional[str] = None
    needs_practice: Optional[str] = None
    repeat_requested: bool = False


class DayResultsRequest(BaseModel):
    date: str
    blocks: list[BlockResult]


class DayResultsResponse(BaseModel):
    items_marked_done: int
    practice_logs_written: int
    feedback_stored: int
    items_requeued: int


@router.post("/day-results", response_model=DayResultsResponse)
async def day_results(
    payload: DayResultsRequest,
    user_email: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await _resolve_user(db, user_email)
    if not user:
        return DayResultsResponse(
            items_marked_done=0, practice_logs_written=0,
            feedback_stored=0, items_requeued=0,
        )

    log_date = date.fromisoformat(payload.date)
    items_done = 0
    logs_written = 0
    feedback_stored = 0
    items_requeued = 0

    for block in payload.blocks:
        if block.status not in ("done", "partial", "skipped"):
            continue

        item = None
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

        has_feedback = (
            block.confidence is not None
            or block.difficulty is not None
            or block.what_worked
            or block.needs_practice
            or block.repeat_requested
        )
        if has_feedback:
            from uuid import UUID
            track_slug = await _track_slug_for_item(db, block.curriculum_item_id, block.routine_id)
            db.add(BlockFeedback(
                user_id=user.id,
                log_date=log_date,
                block_title=block.title,
                track_slug=track_slug,
                curriculum_item_id=UUID(block.curriculum_item_id) if block.curriculum_item_id else None,
                routine_id=UUID(block.routine_id) if block.routine_id else None,
                status=block.status,
                planned_minutes=block.planned_minutes,
                actual_minutes=int(block.actual_minutes) if block.actual_minutes else None,
                confidence=block.confidence,
                difficulty=block.difficulty,
                what_worked=block.what_worked,
                needs_practice=block.needs_practice,
                repeat_requested=block.repeat_requested,
            ))
            feedback_stored += 1

        if block.repeat_requested and block.curriculum_item_id:
            from uuid import UUID
            requeued = await _requeue_item(db, UUID(block.curriculum_item_id), user.id)
            if requeued:
                items_requeued += 1

    await db.commit()
    return DayResultsResponse(
        items_marked_done=items_done,
        practice_logs_written=logs_written,
        feedback_stored=feedback_stored,
        items_requeued=items_requeued,
    )


# ---------- GET /feedback-summary ----------

class TrackFeedbackSummary(BaseModel):
    track_slug: str
    avg_confidence: Optional[float] = None
    avg_difficulty: Optional[float] = None
    avg_actual_minutes: Optional[int] = None
    avg_planned_minutes: Optional[int] = None
    sample_count: int = 0
    pace_signal: str = "on_track"
    items_needing_review: int = 0


class FeedbackSummaryResponse(BaseModel):
    tracks: list[TrackFeedbackSummary]


@router.get("/feedback-summary", response_model=FeedbackSummaryResponse)
async def feedback_summary(
    user_email: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    user = await _resolve_user(db, user_email)
    if not user:
        return FeedbackSummaryResponse(tracks=[])

    result = await db.execute(
        select(LearningTrack).where(LearningTrack.user_id == user.id)
    )
    tracks = result.scalars().all()

    summaries = []
    for track in tracks:
        adj = await _feedback_adjustments(db, user.id, track.slug)
        review_items = await _items_needing_review(db, user.id, track.slug)

        pace = "on_track"
        if adj["avg_confidence"] and adj["avg_confidence"] >= 4.5:
            pace = "accelerate"
        elif adj["avg_difficulty"] and adj["avg_difficulty"] > 4.0:
            pace = "slow_down"
        elif adj["avg_confidence"] and adj["avg_confidence"] < 2.5:
            pace = "struggling"

        summaries.append(TrackFeedbackSummary(
            track_slug=track.slug,
            avg_confidence=adj["avg_confidence"],
            avg_difficulty=adj["avg_difficulty"],
            avg_actual_minutes=adj["avg_actual"],
            avg_planned_minutes=adj["avg_planned"],
            sample_count=adj["sample_count"],
            pace_signal=pace,
            items_needing_review=len(review_items),
        ))

    return FeedbackSummaryResponse(tracks=summaries)


# ---------- helpers ----------

async def _track_slug_for_item(
    db: AsyncSession,
    curriculum_item_id: Optional[str],
    routine_id: Optional[str],
) -> Optional[str]:
    from uuid import UUID
    if curriculum_item_id:
        result = await db.execute(
            select(LearningTrack.slug)
            .join(CurriculumItem, CurriculumItem.track_id == LearningTrack.id)
            .where(CurriculumItem.id == UUID(curriculum_item_id))
        )
        row = result.first()
        return row[0] if row else None
    if routine_id:
        result = await db.execute(
            select(LearningTrack.slug)
            .join(PracticeRoutine, PracticeRoutine.track_id == LearningTrack.id)
            .where(PracticeRoutine.id == UUID(routine_id))
        )
        row = result.first()
        return row[0] if row else None
    return None


async def _requeue_item(
    db: AsyncSession, item_id, user_id
) -> bool:
    result = await db.execute(
        select(CurriculumItem)
        .join(LearningTrack, CurriculumItem.track_id == LearningTrack.id)
        .where(CurriculumItem.id == item_id, LearningTrack.user_id == user_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        return False
    if item.status == ItemStatus.DONE:
        item.status = ItemStatus.PENDING
        item.completed_at = None
        return True
    return False


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
