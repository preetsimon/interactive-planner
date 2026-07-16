from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.domain import DomainStatus
from app.schemas._converters import UUIDStrMixin


class DomainCreate(BaseModel):
    name: str
    required_assets: list[str] = []


class DomainRead(UUIDStrMixin, BaseModel):
    id: str
    name: str
    score: float
    status: DomainStatus
    required_assets: Optional[list[str]]

    model_config = ConfigDict(from_attributes=True)
