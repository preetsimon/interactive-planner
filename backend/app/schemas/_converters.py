"""Shared pre-validator that coerces UUID objects to strings in Read schemas."""
import uuid
from typing import Any
from pydantic import model_validator


class UUIDStrMixin:
    """Mixin: converts UUID fields to str before Pydantic validation.

    Handles both dict input (from JSON) and ORM object input (from_attributes=True).
    """

    @model_validator(mode="before")
    @classmethod
    def coerce_uuids(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {
                k: str(v) if isinstance(v, uuid.UUID) else v
                for k, v in data.items()
            }
        # ORM object path: convert to dict with UUID strings
        if hasattr(data, "__dict__"):
            result = {}
            for key in cls.model_fields:
                val = getattr(data, key, None)
                if isinstance(val, uuid.UUID):
                    result[key] = str(val)
                else:
                    result[key] = val
            return result
        return data
