from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    store_name = Column(String, nullable=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"), nullable=True)
    date_observed = Column(Date, nullable=True)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    items = relationship("SubmissionItem", back_populates="submission", cascade="all, delete-orphan")
    store = relationship("Store")
    user = relationship("User", back_populates="submissions")
    receipt = relationship("ReceiptRecord")


class SubmissionItem(Base):
    __tablename__ = "submission_items"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    weight_value = Column(Float, nullable=True)
    weight_unit = Column(String, nullable=True)
    item_id = Column(Integer, ForeignKey("grocery_items.id"), nullable=True)

    submission = relationship("Submission", back_populates="items")
    item = relationship("GroceryItem")
