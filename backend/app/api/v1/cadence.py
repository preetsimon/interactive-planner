from typing import Optional
import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.quarter import Quarter
from app.schemas.quarter import QuarterCreate, QuarterRead
from app.services.cadence import get_current_quarter, create_quarter, tick

router = APIRouter(prefix="/cadence", tags=["cadence"])


@router.get("/current", response_model=Optional[QuarterRead])
async def current_cadence(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await get_current_quarter(db, user.id)


@router.post("/quarters", response_model=QuarterRead, status_code=201)
async def create_next_quarter(
    payload: QuarterCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await create_quarter(db, user.id, payload.year, payload.quarter_num, payload.theme)


@router.post("/tick")
async def cadence_tick(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    quarter = await tick(db, user.id)
    if not quarter:
        raise HTTPException(status_code=404, detail="No active quarter")
    return QuarterRead.model_validate(quarter)
