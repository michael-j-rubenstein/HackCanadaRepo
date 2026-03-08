from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.database import Base


class Store(Base):
    __tablename__ = "stores"

    store_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)

    products = relationship("ProductItem", back_populates="store")
