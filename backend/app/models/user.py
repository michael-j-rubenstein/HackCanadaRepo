from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=True)
    trust_score = Column(Float, default=1.0)
    submission_count = Column(Integer, default=0)
    home_lat = Column(Float, nullable=True)
    home_lng = Column(Float, nullable=True)
    radius_km = Column(Integer, default=10)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    submissions = relationship("Submission", back_populates="user")
    receipts = relationship("ReceiptRecord", back_populates="user")
