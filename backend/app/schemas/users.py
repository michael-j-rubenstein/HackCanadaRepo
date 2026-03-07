from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: str
    username: Optional[str] = None


class UserUpdate(BaseModel):
    home_lat: Optional[float] = None
    home_lng: Optional[float] = None
    radius_km: Optional[int] = None


class UserOut(BaseModel):
    id: int
    email: str
    username: Optional[str] = None
    trust_score: float
    submission_count: int
    home_lat: Optional[float] = None
    home_lng: Optional[float] = None
    radius_km: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
