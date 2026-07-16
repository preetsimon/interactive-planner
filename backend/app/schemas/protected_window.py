from typing import Optional
from datetime import time
from pydantic import BaseModel, ConfigDict
from app.schemas._converters import UUIDStrMixin


class ProtectedWindowCreate(BaseModel):
    start_time: time
    end_time: time
    days_of_week: list[int] = []
    allowed_category_ids: list[str] = []
    active: bool = True


class ProtectedWindowRead(UUIDStrMixin, BaseModel):
    id: str
    start_time: time
    end_time: time
    days_of_week: Optional[list[int]]
    allowed_category_ids: Optional[list[str]]
    active: bool

    model_config = ConfigDict(from_attributes=True)
