from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PriceAlertCreate(BaseModel):
    item_id: int
    target_price: float


class PriceAlertOut(BaseModel):
    id: int
    item_id: int
    item_name: Optional[str] = None
    target_price: float
    is_triggered: bool
    triggered_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
