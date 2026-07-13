import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.time_block import TimeBlock
from app.schemas.time_block import TimeBlockCreate, TimeBlockRead
from app.services.block_guard import apply_block_guard

router = APIRouter(prefix="/time-blocks", tags=["time-blocks"])


@router.post("", response_model=TimeBlockRead, status_code=status.HTTP_201_CREATED)
async def create_time_block(
    payload: TimeBlockCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    block = TimeBlock(
        user_id=user.id,
        category_id=uuid.UUID(payload.category_id),
        start_at=payload.start_at,
        end_at=payload.end_at,
        notes=payload.notes,
    )
    db.add(block)
    await db.flush()

    block = await apply_block_guard(db, block)
    return block


@router.get("", response_model=list[TimeBlockRead])
async def list_time_blocks(
    from_date: datetime | None = Query(None, alias="from"),
    to_date: datetime | None = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(TimeBlock).where(TimeBlock.user_id == user.id)
    if from_date:
        stmt = stmt.where(TimeBlock.start_at >= from_date)
    if to_date:
        stmt = stmt.where(TimeBlock.start_at <= to_date)
    stmt = stmt.order_by(TimeBlock.start_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.delete("/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_block(
    block_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(TimeBlock).where(TimeBlock.id == block_id, TimeBlock.user_id == user.id)
    )
    block = result.scalar_one_or_none()
    if not block:
        raise HTTPException(status_code=404, detail="Time block not found")
    await db.delete(block)
    await db.commit()
