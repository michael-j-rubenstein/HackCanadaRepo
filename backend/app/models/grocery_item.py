from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class GroceryItem(Base):
    __tablename__ = "grocery_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    unit = Column(String, nullable=False, default="each")
    image_url = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    weight_value = Column(Float, nullable=True)
    weight_unit = Column(String, nullable=True)
    external_id = Column(String, nullable=True)
    barcode = Column(String, nullable=True, unique=True)
    status = Column(String, default="active")
    is_new = Column(Boolean, default=True)
    confirmation_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("Category", back_populates="items")
    price_submissions = relationship("PriceSubmission", back_populates="item", order_by="PriceSubmission.date_observed.desc()")
    price_alerts = relationship("PriceAlert", back_populates="item")
    cart_entries = relationship("ShoppingCartItem", back_populates="item")
    pin_entries = relationship("PinnedItem", back_populates="item")
