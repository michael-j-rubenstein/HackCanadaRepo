from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.price_submission import PriceSubmission
from app.models.submission import Submission


def check_submission_rate(user_id: int, db: Session):
    """Raise 429 if user has > 20 submissions in the last hour."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
    count = (
        db.query(Submission)
        .filter(Submission.user_id == user_id, Submission.created_at >= cutoff)
        .count()
    )
    if count >= 20:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: max 20 submissions per hour",
        )


def check_product_cooldown(user_id: int, product_id: int, db: Session) -> bool:
    """Return True if user already submitted for this product in last 24h."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    count = (
        db.query(PriceSubmission)
        .filter(
            PriceSubmission.user_id == user_id,
            PriceSubmission.item_id == product_id,
            PriceSubmission.submitted_at >= cutoff,
        )
        .count()
    )
    return count > 0
