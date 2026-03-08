from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class ProductItem(Base):
    __tablename__ = "product_items"

    p_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    c_id = Column(String, ForeignKey("categories.c_id"), nullable=False)
    brand_id = Column(String, ForeignKey("brands.brand_id"), nullable=False)
    store_id = Column(String, ForeignKey("stores.store_id"), nullable=False)

    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    store = relationship("Store", back_populates="products")
    submission_items = relationship("SubmissionItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    price_history = relationship("PriceByHour", back_populates="product")
