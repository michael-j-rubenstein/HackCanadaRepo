from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class PriceSubmission(Base):
    __tablename__ = "price_submissions"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("grocery_items.id"), nullable=False)
    price = Column(Float, nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    date_observed = Column(Date, nullable=False)
    weight_value = Column(Float, nullable=True)
    weight_unit = Column(String, nullable=True)
    price_per_100g = Column(Float, nullable=True)
    report_type = Column(String, default="community")
    source = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"), nullable=True)
    confidence = Column(Float, default=1.0)
    is_verified = Column(Boolean, default=False)
    is_outlier = Column(Boolean, default=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("GroceryItem", back_populates="price_submissions")
    store = relationship("Store", back_populates="price_submissions")
    user = relationship("User")
    receipt = relationship("ReceiptRecord")
