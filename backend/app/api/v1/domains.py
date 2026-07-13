import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.domain import TargetDomain
from app.schemas.domain import DomainCreate, DomainRead
from app.services.niche_filter import score_all

router = APIRouter(prefix="/domains", tags=["domains"])


@router.get("", response_model=list[DomainRead])
async def list_domains(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(TargetDomain)
        .where(TargetDomain.user_id == user.id)
        .order_by(TargetDomain.score.desc())
    )
    return result.scalars().all()


@router.post("", response_model=DomainRead, status_code=201)
async def create_domain(
    payload: DomainCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    domain = TargetDomain(
        user_id=user.id,
        name=payload.name,
        required_assets=payload.required_assets,
    )
    db.add(domain)
    await db.commit()
    await db.refresh(domain)
    return domain


@router.post("/rescore", response_model=list[DomainRead])
async def rescore_domains(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await score_all(db, user.id)
