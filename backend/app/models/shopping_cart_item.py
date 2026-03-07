from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ShoppingCartItem(Base):
    __tablename__ = "shopping_cart_items"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("grocery_items.id"), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("GroceryItem", back_populates="cart_entries")
