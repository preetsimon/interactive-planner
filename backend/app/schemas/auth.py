from typing import Optional
from pydantic import BaseModel, EmailStr
from app.schemas._converters import UUIDStrMixin


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    stated_goal: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(UUIDStrMixin, BaseModel):
    id: str
    email: str
    stated_goal: Optional[str]
    weekly_goal_hours_threshold: int

    model_config = {"from_attributes": True}
