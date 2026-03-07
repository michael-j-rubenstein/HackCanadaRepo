import logging

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import text

from app.database import SessionLocal

logger = logging.getLogger(__name__)


def refresh_materialized_views():
    """Refresh all materialized views."""
    db = SessionLocal()
    try:
        db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_product_price_daily"))
        db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_category_price_daily"))
        db.commit()
        logger.info("Materialized views refreshed successfully")
    except Exception as e:
        logger.warning(f"Failed to refresh materialized views (may not exist yet): {e}")
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    """Start the APScheduler background scheduler."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_materialized_views, "interval", minutes=15, id="refresh_views")
    scheduler.start()
    logger.info("APScheduler started: refreshing materialized views every 15 minutes")
    return scheduler
