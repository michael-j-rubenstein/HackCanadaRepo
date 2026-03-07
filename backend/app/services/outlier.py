import math
from datetime import date, timedelta

from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from app.models.price_submission import PriceSubmission


def check_outlier(db: Session, item_id: int, price: float, store_id: int | None = None) -> bool:
    """Return True if price is > 2 std deviations from 30-day mean for this item."""
    cutoff = date.today() - timedelta(days=30)
    q = (
        db.query(
            sa_func.avg(PriceSubmission.price).label("mean"),
            sa_func.count(PriceSubmission.id).label("cnt"),
        )
        .filter(
            PriceSubmission.item_id == item_id,
            PriceSubmission.date_observed >= cutoff,
            PriceSubmission.is_outlier == False,
        )
    )
    row = q.one()
    if not row.mean or row.cnt < 5:
        return False

    # Compute stddev
    stddev_row = (
        db.query(
            sa_func.sqrt(
                sa_func.avg(sa_func.pow(PriceSubmission.price - row.mean, 2))
            ).label("stddev")
        )
        .filter(
            PriceSubmission.item_id == item_id,
            PriceSubmission.date_observed >= cutoff,
            PriceSubmission.is_outlier == False,
        )
        .one()
    )
    stddev = stddev_row.stddev or 0
    if stddev == 0:
        return False

    return abs(price - row.mean) > 2 * stddev
