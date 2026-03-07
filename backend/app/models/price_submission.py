from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class PriceSubmission(Base):
    __tablename__ = "price_submissions"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("grocery_items.id"), nullable=False)
    price = Column(Float, nullable=False)
    store_name = Column(String, nullable=False)
    date_observed = Column(Date, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("GroceryItem", back_populates="price_submissions")
