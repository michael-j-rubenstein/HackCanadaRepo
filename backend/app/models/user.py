from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    u_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)

    submissions = relationship("Submission", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")
