from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PinnedItemCreate(BaseModel):
    item_id: int


class PinnedItemOut(BaseModel):
    id: int
    item_id: int
    item_name: Optional[str] = None
    current_price: Optional[float] = None
    price_change_pct: Optional[float] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
