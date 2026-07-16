from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas._converters import UUIDStrMixin


class TimeBlockCreate(BaseModel):
    category_id: str
    start_at: datetime
    end_at: datetime
    notes: Optional[str] = None


class TimeBlockRead(UUIDStrMixin, BaseModel):
    id: str
    category_id: str
    start_at: datetime
    end_at: datetime
    notes: Optional[str]
    violates_protected_window: bool
    violates_cutoff: bool

    model_config = ConfigDict(from_attributes=True)
