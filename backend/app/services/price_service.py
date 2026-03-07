from datetime import datetime, timedelta, date, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.grocery_item import GroceryItem
from app.models.price_submission import PriceSubmission
from app.models.price_alert import PriceAlert


def recalculate_current_price(db: Session, item_id: int) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    recent_avg = (
        db.query(func.avg(PriceSubmission.price))
        .filter(
            PriceSubmission.item_id == item_id,
            PriceSubmission.submitted_at >= cutoff,
        )
        .scalar()
    )
    if recent_avg is None:
        return

    item = db.query(GroceryItem).filter(GroceryItem.id == item_id).first()
    if not item:
        return

    old_price = item.current_price
    item.current_price = round(recent_avg, 2)

    if old_price and old_price > 0:
        item.price_change_pct = round(
            ((item.current_price - old_price) / old_price) * 100, 2
        )
    else:
        item.price_change_pct = 0.0

    db.commit()


def check_alerts(db: Session, item_id: int) -> None:
    item = db.query(GroceryItem).filter(GroceryItem.id == item_id).first()
    if not item or item.current_price is None:
        return

    alerts = (
        db.query(PriceAlert)
        .filter(
            PriceAlert.item_id == item_id,
            PriceAlert.is_triggered == False,
        )
        .all()
    )

    now = datetime.now(timezone.utc)
    for alert in alerts:
        if item.current_price <= alert.target_price:
            alert.is_triggered = True
            alert.triggered_at = now

    db.commit()


def get_price_history(
    db: Session, item_id: int, days: int = 30
) -> list[dict]:
    cutoff = date.today() - timedelta(days=days)
    rows = (
        db.query(
            PriceSubmission.date_observed,
            func.avg(PriceSubmission.price).label("avg_price"),
        )
        .filter(
            PriceSubmission.item_id == item_id,
            PriceSubmission.date_observed >= cutoff,
        )
        .group_by(PriceSubmission.date_observed)
        .order_by(PriceSubmission.date_observed)
        .all()
    )
    return [
        {"date": row.date_observed.isoformat(), "avg_price": round(row.avg_price, 2)}
        for row in rows
    ]
