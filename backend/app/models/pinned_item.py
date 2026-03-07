from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class PinnedItem(Base):
    __tablename__ = "pinned_items"
    __table_args__ = (UniqueConstraint("user_id", "item_id", name="uq_pin_user_item"),)

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("grocery_items.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("GroceryItem", back_populates="pin_entries")
    user = relationship("User")
