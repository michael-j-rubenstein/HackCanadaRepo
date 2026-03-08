import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from app.database import SessionLocal
from app.models.submission import Submission
from app.models.submission_item import SubmissionItem
from app.models.price_by_hour import PriceByHour

logger = logging.getLogger(__name__)


def aggregate_hourly_prices():
    """Aggregate submission prices from the last hour into price_by_hour."""
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        one_hour_ago = now - timedelta(hours=1)
        hour_truncated = now.replace(minute=0, second=0, microsecond=0)

        results = (
            db.query(
                SubmissionItem.p_id,
                func.avg(SubmissionItem.price).label("avg_price"),
            )
            .join(Submission, SubmissionItem.sub_id == Submission.sub_id)
            .filter(
                Submission.is_confirmed == True,
                Submission.created_at >= one_hour_ago,
                Submission.created_at <= now,
            )
            .group_by(SubmissionItem.p_id)
            .all()
        )

        if not results:
            logger.info("No confirmed submissions in the last hour, skipping.")
            return

        for p_id, avg_price in results:
            existing = (
                db.query(PriceByHour)
                .filter(
                    PriceByHour.p_id == p_id,
                    PriceByHour.timestamp == hour_truncated,
                )
                .first()
            )
            if existing is None:
                db.add(PriceByHour(
                    p_id=p_id,
                    timestamp=hour_truncated,
                    price=round(avg_price, 2),
                ))

        db.commit()
        logger.info(
            "Aggregated prices for %d products at %s", len(results), hour_truncated
        )
    except Exception:
        db.rollback()
        logger.exception("Error during hourly price aggregation")
    finally:
        db.close()
