from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas._converters import UUIDStrMixin


class TimeBlockCreate(BaseModel):
    category_id: str
    start_at: datetime
    end_at: datetime
    notes: str | None = None


class TimeBlockRead(UUIDStrMixin, BaseModel):
    id: str
    category_id: str
    start_at: datetime
    end_at: datetime
    notes: str | None
    violates_protected_window: bool
    violates_cutoff: bool

    model_config = ConfigDict(from_attributes=True)
