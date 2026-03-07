from pydantic import BaseModel


class ReceiptItem(BaseModel):
    name: str
    category: str | None = None
    quantity: int
    unit_price: float
    total_price: float
    weight_value: float | None = None
    weight_unit: str | None = None


class ReceiptData(BaseModel):
    store_name: str | None = None
    store_address: str | None = None
    date: str | None = None
    items: list[ReceiptItem]
    subtotal: float | None = None
    tax: float | None = None
    total: float
