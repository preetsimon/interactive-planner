from typing import Optional
import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.audit import AuditReport, AuditLogEntry
from app.schemas.audit import AuditReportRead, AuditLogEntryRead

router = APIRouter(tags=["audits"])


@router.get("/reports", response_model=list[AuditReportRead])
async def list_reports(
    report_type: Optional[str] = Query(None, alias="type"),
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(AuditReport).where(AuditReport.user_id == user.id)
    if report_type:
        stmt = stmt.where(AuditReport.type == report_type)
    if from_date:
        stmt = stmt.where(AuditReport.period_start >= from_date)
    if to_date:
        stmt = stmt.where(AuditReport.period_end <= to_date)
    result = await db.execute(stmt.order_by(AuditReport.period_start.desc()))
    return result.scalars().all()


@router.get("/audit-log", response_model=list[AuditLogEntryRead])
async def list_audit_log(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(AuditLogEntry).where(AuditLogEntry.user_id == user.id)
    if from_date:
        stmt = stmt.where(AuditLogEntry.occurred_at >= from_date.isoformat())
    if to_date:
        stmt = stmt.where(AuditLogEntry.occurred_at <= to_date.isoformat())
    result = await db.execute(stmt.order_by(AuditLogEntry.occurred_at.desc()))
    return result.scalars().all()
