from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class CategoryOut(BaseModel):
    id: int
    name: str
    icon: Optional[str] = None

    model_config = {"from_attributes": True}


class StoreOut(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None

    model_config = {"from_attributes": True}


class GroceryItemOut(BaseModel):
    id: int
    name: str
    brand: Optional[str] = None
    unit: str
    weight_value: Optional[float] = None
    weight_unit: Optional[str] = None
    price_per_100g: Optional[float] = None
    image_url: Optional[str] = None
    category_id: int
    category_name: Optional[str] = None
    current_price: Optional[float] = None
    external_id: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StorePriceOut(BaseModel):
    store_id: int
    store_name: str
    price: float
    price_per_100g: Optional[float] = None
    date_observed: date


class PricePointOut(BaseModel):
    date: str
    avg_price: float
