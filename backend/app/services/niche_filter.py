"""Niche Filter — scores job-search domains against core assets."""
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import TargetDomain, DomainStatus


async def score_all(db: AsyncSession, user_id: uuid.UUID) -> list[TargetDomain]:
    result = await db.execute(
        select(TargetDomain).where(TargetDomain.user_id == user_id)
    )
    domains = result.scalars().all()

    for domain in domains:
        required = set(domain.required_assets or [])
        # For now, score is based on presence — no weights in v1
        # This is simplified; real implementation would use core_assets table
        if required:
            domain.score = min(len(required) / max(len(required), 1), 1.0)
        else:
            domain.score = 0.0

        if domain.score < 0.5:
            domain.status = DomainStatus.CUT

    await db.commit()
    return list(domains)
