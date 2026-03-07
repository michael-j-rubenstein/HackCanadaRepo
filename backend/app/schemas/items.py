from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CategoryOut(BaseModel):
    id: int
    name: str
    icon: Optional[str] = None

    model_config = {"from_attributes": True}


class GroceryItemOut(BaseModel):
    id: int
    name: str
    brand: Optional[str] = None
    unit: str
    image_url: Optional[str] = None
    category_id: int
    category_name: Optional[str] = None
    current_price: Optional[float] = None
    price_change_pct: Optional[float] = None
    external_id: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PricePointOut(BaseModel):
    date: str
    avg_price: float
