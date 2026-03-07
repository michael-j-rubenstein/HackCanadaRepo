from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ReceiptRecord(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ocr_parsed_json = Column(JSON, nullable=True)
    store_location_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    purchase_date = Column(Date, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="receipts")
    store = relationship("Store")
