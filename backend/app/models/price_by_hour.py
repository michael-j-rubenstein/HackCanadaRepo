from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class PriceByHour(Base):
    __tablename__ = "price_by_hour"

    p_id = Column(String, ForeignKey("product_items.p_id"), primary_key=True)
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    price = Column(Float, nullable=False)

    product = relationship("ProductItem", back_populates="price_history")
