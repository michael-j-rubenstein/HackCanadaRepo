from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ShoppingCartItemCreate(BaseModel):
    item_id: int


class ShoppingCartItemOut(BaseModel):
    id: int
    item_id: int
    item_name: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
