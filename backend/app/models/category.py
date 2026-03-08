from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    c_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    unit = Column(String, nullable=False)

    products = relationship("ProductItem", back_populates="category")
