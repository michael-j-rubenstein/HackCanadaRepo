from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class SubmissionItemOut(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    quantity: int
    unit_price: float
    total_price: float
    weight_value: Optional[float] = None
    weight_unit: Optional[str] = None
    item_id: Optional[int] = None
    item_name: Optional[str] = None
    is_valid: bool = False

    model_config = {"from_attributes": True}


class SubmissionItemIn(BaseModel):
    id: Optional[int] = None
    name: str
    category: Optional[str] = None
    quantity: int = 1
    unit_price: float
    total_price: float
    weight_value: Optional[float] = None
    weight_unit: Optional[str] = None
    item_id: Optional[int] = None


class SubmissionUpdate(BaseModel):
    store_name: Optional[str] = None
    date_observed: Optional[date] = None
    items: list[SubmissionItemIn]


class SubmissionOut(BaseModel):
    id: int
    store_name: Optional[str] = None
    date_observed: Optional[date] = None
    status: str
    created_at: Optional[datetime] = None
    items: list[SubmissionItemOut] = []

    model_config = {"from_attributes": True}
