from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.database import Base


class Brand(Base):
    __tablename__ = "brands"

    brand_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)

    products = relationship("ProductItem", back_populates="brand")
