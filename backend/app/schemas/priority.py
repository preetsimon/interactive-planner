from pydantic import BaseModel, ConfigDict, Field

from app.models.priority import PriorityTrack, PriorityStatus
from app.schemas._converters import UUIDStrMixin


class PriorityCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    track: PriorityTrack
    definition_of_done: str = Field(min_length=1)


class PriorityRead(UUIDStrMixin, BaseModel):
    id: str
    title: str
    track: PriorityTrack
    status: PriorityStatus
    definition_of_done: str

    model_config = ConfigDict(from_attributes=True)


class PriorityCapError(BaseModel):
    error: str = "PRIORITY_CAP"
    message: str
    blocking_priority: dict
