from typing import Optional
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.learning import ItemStatus
from app.schemas._converters import UUIDStrMixin


class CurriculumItemRead(UUIDStrMixin, BaseModel):
    id: str
    section: str
    title: str
    details: Optional[str] = None
    learning_goal: Optional[str] = None
    key_topics: Optional[list[str]] = None
    sort_order: int
    status: ItemStatus
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RoutineStatusRead(UUIDStrMixin, BaseModel):
    id: str
    name: str
    minutes: Optional[int] = None
    rest_weekdays: list[int]
    is_rest_today: bool
    today_done: bool
    today_minutes: Optional[int] = None
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
    log_date: Optional[date] = None
    minutes: Optional[int] = Field(None, ge=0, le=1440)


class PracticeLogRead(UUIDStrMixin, BaseModel):
    id: str
    routine_id: str
    log_date: date
    minutes: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
