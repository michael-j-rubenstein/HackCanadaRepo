from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class PriceSubmissionCreate(BaseModel):
    price: float
    store_name: str
    date_observed: date


class PriceSubmissionOut(BaseModel):
    id: int
    item_id: int
    price: float
    store_name: str
    date_observed: date
    submitted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
