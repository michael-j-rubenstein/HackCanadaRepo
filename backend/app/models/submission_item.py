from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class SubmissionItem(Base):
    __tablename__ = "submission_items"

    sub_item_id = Column(String, primary_key=True, index=True)
    p_id = Column(String, ForeignKey("product_items.p_id"), nullable=False)
    sub_id = Column(String, ForeignKey("submissions.sub_id"), nullable=False)
    price = Column(Float, nullable=False)

    product = relationship("ProductItem", back_populates="submission_items")
    submission = relationship("Submission", back_populates="items")
