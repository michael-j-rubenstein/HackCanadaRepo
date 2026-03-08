from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    u_id = Column(String, ForeignKey("users.u_id"), primary_key=True)
    p_id = Column(String, ForeignKey("product_items.p_id"), primary_key=True)

    user = relationship("User", back_populates="cart_items")
    product = relationship("ProductItem", back_populates="cart_items")
