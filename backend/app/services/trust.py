from sqlalchemy import case, func as sa_func
from sqlalchemy.orm import Session

from app.models.price_submission import PriceSubmission
from app.models.user import User


def recompute_trust_score(db: Session, user_id: int) -> float:
    """Recompute trust score based on user's submission history."""
    stats = (
        db.query(
            sa_func.count(PriceSubmission.id).label("total"),
            sa_func.sum(case((PriceSubmission.is_outlier == True, 1), else_=0)).label("outlier_count"),
            sa_func.sum(case((PriceSubmission.is_verified == True, 1), else_=0)).label("verified_count"),
        )
        .filter(PriceSubmission.user_id == user_id)
        .one()
    )

    total = stats.total or 0
    outlier_count = int(stats.outlier_count or 0)
    verified_count = int(stats.verified_count or 0)

    if total == 0:
        score = 1.0
    else:
        outlier_rate = outlier_count / total
        verified_bonus = min(verified_count / total * 0.2, 0.2)
        score = max(0.1, min(2.0, 1.0 * (1 - outlier_rate) * (1 + verified_bonus)))

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.trust_score = round(score, 3)
        user.submission_count = total
        db.flush()

    return score
