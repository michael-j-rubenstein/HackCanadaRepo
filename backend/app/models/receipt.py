from pydantic import BaseModel
from typing import Optional


class ReceiptItem(BaseModel):
    name: str
    total_price: float
    category: Optional[str] = None
    weight_value: Optional[float] = None
    weight_unit: Optional[str] = None


class ReceiptData(BaseModel):
    store_name: Optional[str] = None
    date: Optional[str] = None
    items: list[ReceiptItem] = []
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
