from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.learning import ItemStatus
from app.schemas._converters import UUIDStrMixin


class CurriculumItemRead(UUIDStrMixin, BaseModel):
    id: str
    section: str
    title: str
    details: str | None = None
    sort_order: int
    status: ItemStatus
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class RoutineStatusRead(UUIDStrMixin, BaseModel):
    id: str
    name: str
    minutes: int | None = None
    rest_weekdays: list[int]
    is_rest_today: bool
    today_done: bool
    today_minutes: int | None = None
    streak: int

    model_config = ConfigDict(from_attributes=True)


class TrackRead(UUIDStrMixin, BaseModel):
    id: str
    slug: str
    name: str
    description: str
    items_total: int
    items_done: int

    model_config = ConfigDict(from_attributes=True)


class TrackDetailRead(TrackRead):
    items: list[CurriculumItemRead]
    routines: list[RoutineStatusRead]


class PracticeLogCreate(BaseModel):
    log_date: date | None = None
    minutes: int | None = Field(None, ge=0, le=1440)


class PracticeLogRead(UUIDStrMixin, BaseModel):
    id: str
    routine_id: str
    log_date: date
    minutes: int | None = None

    model_config = ConfigDict(from_attributes=True)
