from typing import Optional
from datetime import date
from pydantic import BaseModel, ConfigDict

from app.models.quarter import Phase
from app.schemas._converters import UUIDStrMixin


class QuarterCreate(BaseModel):
    year: int
    quarter_num: int
    theme: str = ""


class QuarterRead(UUIDStrMixin, BaseModel):
    id: str
    year: int
    quarter_num: int
    theme: str
    phase: Phase
    sprint_start: Optional[date]
    sprint_end: Optional[date]

    model_config = ConfigDict(from_attributes=True)
