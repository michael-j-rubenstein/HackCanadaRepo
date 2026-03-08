from sqlalchemy import Column, String, ForeignKey, JSON, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    sub_id = Column(String, primary_key=True, index=True)
    u_id = Column(String, ForeignKey("users.u_id"), nullable=False)
    receipt = Column(JSON, nullable=True)
    is_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="submissions")
    items = relationship("SubmissionItem", back_populates="submission")
