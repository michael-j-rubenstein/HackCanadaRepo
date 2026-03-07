from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
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
    current_price = Column(Float, nullable=True)
    price_change_pct = Column(Float, nullable=True, default=0.0)
    external_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("Category", back_populates="items")
    price_submissions = relationship("PriceSubmission", back_populates="item")
    price_alerts = relationship("PriceAlert", back_populates="item")
