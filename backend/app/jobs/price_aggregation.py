import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from app.database import SessionLocal
from app.models.product_item import ProductItem
from app.models.submission import Submission
from app.models.submission_item import SubmissionItem
from app.models.price_by_hour import PriceByHour

logger = logging.getLogger(__name__)


def aggregate_hourly_prices():
    """Aggregate submission prices from the last hour into price_by_hour.

    For products with new confirmed submissions, the average submitted price
    is stored.  For products with NO new submissions, the most recent known
    price is carried forward so the frontend always has a value.
    """
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        one_hour_ago = now - timedelta(hours=1)
        hour_truncated = now.replace(minute=0, second=0, microsecond=0)

        # ── 1. Aggregate new submissions ──
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

        updated_pids = set()
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
                updated_pids.add(p_id)

        # ── 2. Carry forward previous price for products with no new submissions ──
        all_pids = [row[0] for row in db.query(ProductItem.p_id).all()]

        carried = 0
        for p_id in all_pids:
            if p_id in updated_pids:
                continue
            # Skip if this hour already has a row
            already = (
                db.query(PriceByHour)
                .filter(
                    PriceByHour.p_id == p_id,
                    PriceByHour.timestamp == hour_truncated,
                )
                .first()
            )
            if already:
                continue
            # Get the most recent price
            latest = (
                db.query(PriceByHour)
                .filter(PriceByHour.p_id == p_id)
                .order_by(PriceByHour.timestamp.desc())
                .first()
            )
            if latest:
                db.add(PriceByHour(
                    p_id=p_id,
                    timestamp=hour_truncated,
                    price=latest.price,
                ))
                carried += 1

        db.commit()
        logger.info(
            "Aggregated prices for %d products (%d new, %d carried forward) at %s",
            len(updated_pids) + carried, len(updated_pids), carried, hour_truncated,
        )
    except Exception:
        db.rollback()
        logger.exception("Error during hourly price aggregation")
    finally:
        db.close()
