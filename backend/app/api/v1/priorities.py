from typing import Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.priority import Priority, PriorityStatus
from app.schemas.priority import PriorityCreate, PriorityRead
from app.services.priority_gate import add_priority, cut_priority, complete_priority, PriorityCapError

router = APIRouter(prefix="/priorities", tags=["priorities"])


@router.post("", response_model=PriorityRead, status_code=status.HTTP_201_CREATED)
async def create_priority(
    payload: PriorityCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await add_priority(db, user.id, payload)
    except PriorityCapError as e:
        bp = e.blocking_priority
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "PRIORITY_CAP",
                "message": f"1 active {payload.track.value} priority allowed. Cut or complete the existing one first.",
                "blocking_priority": {"id": str(bp.id), "title": bp.title},
            },
        )


@router.get("", response_model=list[PriorityRead])
async def list_priorities(
    status_filter: Optional[PriorityStatus] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(Priority).where(Priority.user_id == user.id)
    if status_filter:
        stmt = stmt.where(Priority.status == status_filter)
    result = await db.execute(stmt.order_by(Priority.created_at.desc()))
    return result.scalars().all()


@router.post("/{priority_id}/cut", response_model=PriorityRead)
async def cut(
    priority_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Priority).where(Priority.id == priority_id, Priority.user_id == user.id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Priority not found")
    return await cut_priority(db, priority_id)


@router.post("/{priority_id}/complete", response_model=PriorityRead)
async def complete(
    priority_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Priority).where(Priority.id == priority_id, Priority.user_id == user.id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Priority not found")
    return await complete_priority(db, priority_id)
