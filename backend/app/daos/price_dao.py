from datetime import date
from difflib import SequenceMatcher

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.grocery_item import GroceryItem
from app.models.price_submission import PriceSubmission
from app.models.store import Store

_FUZZY_THRESHOLD = 0.5


class PriceDAO:
    def __init__(self, db: Session):
        self.db = db

    def find_item(self, name: str, category: str | None = None) -> tuple[GroceryItem | None, float]:
        """Return (matched_item, confidence_ratio). Confidence is 1.0 for exact/substring, else the fuzzy ratio."""
        query = self.db.query(GroceryItem)
        if category:
            query = query.join(Category).filter(Category.name.ilike(category))

        # Try substring match first
        result = query.filter(GroceryItem.name.ilike(f"%{name}%")).first()
        if result:
            return (result, 1.0)

        # Fall back to fuzzy matching
        candidates = query.all()
        best_match = None
        best_ratio = 0.0
        name_lower = name.lower()
        for item in candidates:
            ratio = SequenceMatcher(None, name_lower, item.name.lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = item

        if best_ratio >= _FUZZY_THRESHOLD:
            return (best_match, best_ratio)
        return (None, 0.0)

    def get_or_create_store(self, name: str) -> Store:
        store = self.db.query(Store).filter(Store.name == name).first()
        if not store:
            store = Store(name=name)
            self.db.add(store)
            self.db.flush()
        return store

    def create_price_submission(
        self,
        item_id: int,
        price: float,
        store_id: int,
        date_observed: date,
        weight_value: float | None = None,
        weight_unit: str | None = None,
        price_per_100g: float | None = None,
        report_type: str = "community",
        source: str | None = None,
        user_id: int | None = None,
        receipt_id: int | None = None,
        confidence: float = 1.0,
        is_verified: bool = False,
        is_outlier: bool = False,
    ) -> PriceSubmission:
        submission = PriceSubmission(
            item_id=item_id,
            price=price,
            store_id=store_id,
            date_observed=date_observed,
            weight_value=weight_value,
            weight_unit=weight_unit,
            price_per_100g=price_per_100g,
            report_type=report_type,
            source=source,
            user_id=user_id,
            receipt_id=receipt_id,
            confidence=confidence,
            is_verified=is_verified,
            is_outlier=is_outlier,
        )
        self.db.add(submission)
        return submission

    def get_latest_price(self, item_id: int) -> PriceSubmission | None:
        return (
            self.db.query(PriceSubmission)
            .filter(PriceSubmission.item_id == item_id, PriceSubmission.is_outlier == False)
            .order_by(PriceSubmission.date_observed.desc(), PriceSubmission.submitted_at.desc())
            .first()
        )

    def get_latest_prices_by_store(self, item_id: int, store_ids: list[int] | None = None) -> list:
        base_filter = [
            PriceSubmission.item_id == item_id,
            PriceSubmission.is_outlier == False,
        ]
        if store_ids is not None:
            base_filter.append(PriceSubmission.store_id.in_(store_ids))

        latest_sub = (
            self.db.query(
                PriceSubmission.store_id,
                func.max(PriceSubmission.date_observed).label("max_date"),
            )
            .filter(*base_filter)
            .group_by(PriceSubmission.store_id)
            .subquery()
        )

        results = (
            self.db.query(PriceSubmission)
            .join(
                latest_sub,
                (PriceSubmission.store_id == latest_sub.c.store_id)
                & (PriceSubmission.date_observed == latest_sub.c.max_date),
            )
            .filter(PriceSubmission.item_id == item_id, PriceSubmission.is_outlier == False)
            .all()
        )
        return results

    def get_price_history(
        self,
        item_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
        store_ids: list[int] | None = None,
    ) -> list:
        q = (
            self.db.query(
                PriceSubmission.date_observed,
                func.avg(PriceSubmission.price).label("avg_price"),
            )
            .filter(PriceSubmission.item_id == item_id, PriceSubmission.is_outlier == False)
        )
        if start_date:
            q = q.filter(PriceSubmission.date_observed >= start_date)
        if end_date:
            q = q.filter(PriceSubmission.date_observed <= end_date)
        if store_ids is not None:
            q = q.filter(PriceSubmission.store_id.in_(store_ids))

        return (
            q.group_by(PriceSubmission.date_observed)
            .order_by(PriceSubmission.date_observed)
            .all()
        )

    def commit(self):
        self.db.commit()

    def refresh(self, obj):
        self.db.refresh(obj)
