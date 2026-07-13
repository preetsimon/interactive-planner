from datetime import date
from pydantic import BaseModel, ConfigDict

from app.models.deadline import DeadlineStatus
from app.schemas._converters import UUIDStrMixin


class DeadlineRead(UUIDStrMixin, BaseModel):
    id: str
    priority_id: str
    due_date: date
    status: DeadlineStatus

    model_config = ConfigDict(from_attributes=True)


class ScopeCutCreate(BaseModel):
    description: str
