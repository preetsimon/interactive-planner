from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

from app.models.audit import AuditType, Verdict
from app.schemas._converters import UUIDStrMixin


class AuditReportRead(UUIDStrMixin, BaseModel):
    id: str
    type: AuditType
    period_start: date
    period_end: date
    verdict: Verdict
    payload: Optional[dict]

    model_config = ConfigDict(from_attributes=True)


class AuditLogEntryRead(UUIDStrMixin, BaseModel):
    id: str
    event_type: str
    entity_type: str
    entity_id: Optional[str]
    detail: Optional[dict]
    occurred_at: datetime

    model_config = ConfigDict(from_attributes=True)
