from datetime import date

from sqlalchemy.orm import Session

from app.clients.gemini import extract_receipt
from app.daos.price_dao import PriceDAO
from app.models.category import Category
from app.models.grocery_item import GroceryItem
from app.models.price_submission import PriceSubmission
from app.models.receipt import ReceiptData
from app.models.receipt_record import ReceiptRecord
from app.models.submission import Submission, SubmissionItem
from app.models.user import User
from app.schemas.items import PricePointOut, StorePriceOut
from app.services.geo import get_store_ids_in_radius
from app.services.outlier import check_outlier
from app.services.trust import recompute_trust_score
from app.services.unit_conversion import compute_price_per_100g


def get_latest_price(db: Session, item_id: int) -> float | None:
    dao = PriceDAO(db)
    sub = dao.get_latest_price(item_id)
    return sub.price if sub else None


def get_price_history(
    db: Session,
    item_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
    lat: float | None = None,
    lng: float | None = None,
    radius_km: float | None = None,
) -> list[PricePointOut]:
    dao = PriceDAO(db)
    store_ids = None
    if lat is not None and lng is not None and radius_km is not None:
        store_ids = get_store_ids_in_radius(db, lat, lng, radius_km)
    rows = dao.get_price_history(item_id, start_date, end_date, store_ids=store_ids)
    return [
        PricePointOut(date=str(row.date_observed), avg_price=round(row.avg_price, 2))
        for row in rows
    ]


def get_store_prices(
    db: Session,
    item_id: int,
    lat: float | None = None,
    lng: float | None = None,
    radius_km: float | None = None,
) -> list[StorePriceOut]:
    dao = PriceDAO(db)
    item = db.query(GroceryItem).filter(GroceryItem.id == item_id).first()
    if not item:
        return []

    store_ids = None
    if lat is not None and lng is not None and radius_km is not None:
        store_ids = get_store_ids_in_radius(db, lat, lng, radius_km)

    submissions = dao.get_latest_prices_by_store(item_id, store_ids=store_ids)
    results = []
    for sub in submissions:
        pp100g = sub.price_per_100g or compute_price_per_100g(
            sub.price, item.weight_value, item.weight_unit
        )
        results.append(StorePriceOut(
            store_id=sub.store_id,
            store_name=sub.store.name,
            price=sub.price,
            price_per_100g=pp100g,
            date_observed=sub.date_observed,
        ))
    return results


def try_complete_submission(db: Session, submission: Submission) -> bool:
    """Check if all items are valid. If so, create PriceSubmissions and mark completed."""
    if submission.status == "completed":
        return True

    if not submission.items or any(si.item_id is None for si in submission.items):
        return False

    dao = PriceDAO(db)
    store = dao.get_or_create_store(submission.store_name or "Unknown")
    submission.store_id = store.id
    date_observed = submission.date_observed or date.today()

    for si in submission.items:
        item = db.query(GroceryItem).filter(GroceryItem.id == si.item_id).first()
        w_val = si.weight_value or (item.weight_value if item else None)
        w_unit = si.weight_unit or (item.weight_unit if item else None)
        pp100g = compute_price_per_100g(si.unit_price, w_val, w_unit)

        # Determine source
        source = "gemini_ocr" if submission.receipt_id else "manual"

        is_outlier_flag = check_outlier(db, si.item_id, si.unit_price, store.id)

        ps = dao.create_price_submission(
            item_id=si.item_id,
            price=si.unit_price,
            store_id=store.id,
            date_observed=date_observed,
            weight_value=si.weight_value,
            weight_unit=si.weight_unit,
            price_per_100g=pp100g,
            report_type="community",
            source=source,
            user_id=submission.user_id,
            receipt_id=submission.receipt_id,
            confidence=getattr(si, '_match_confidence', 1.0),
            is_outlier=is_outlier_flag,
        )

        if is_outlier_flag:
            print(f"Outlier detected: item={si.item_id} price={si.unit_price}")

    submission.status = "completed"
    db.commit()

    # Recompute trust score
    if submission.user_id:
        recompute_trust_score(db, submission.user_id)
        db.commit()

    return True


class PriceService:
    def __init__(self, db: Session):
        self.db = db
        self.dao = PriceDAO(db)

    def _create_submission(self, receipt: ReceiptData, user_id: int | None = None, receipt_id: int | None = None) -> Submission:
        """Create a Submission with items, auto-match to grocery items, and try to complete."""
        date_observed = date.today()
        if receipt.date:
            try:
                date_observed = date.fromisoformat(receipt.date)
            except ValueError:
                pass

        submission = Submission(
            user_id=user_id,
            store_name=receipt.store_name,
            date_observed=date_observed,
            receipt_id=receipt_id,
            status="pending",
        )
        self.db.add(submission)
        self.db.flush()

        valid_categories = {c.name.lower(): c for c in self.db.query(Category).all()}

        for receipt_item in receipt.items:
            matched, confidence = self.dao.find_item(receipt_item.name, receipt_item.category)

            if matched:
                print(f"Matched '{receipt_item.name}' -> '{matched.name}' (id={matched.id}, confidence={confidence:.2f})")
                # Handle new product confirmation
                if matched.is_new:
                    matched.confirmation_count += 1
                    if matched.confirmation_count >= 3:
                        matched.is_new = False
            else:
                print(f"Unmatched receipt item: '{receipt_item.name}' (category: {receipt_item.category})")
                # New product detection: create item if valid category
                if receipt_item.category and receipt_item.category.lower() in valid_categories:
                    cat = valid_categories[receipt_item.category.lower()]
                    matched = GroceryItem(
                        name=receipt_item.name,
                        unit="each",
                        category_id=cat.id,
                        is_new=True,
                        confirmation_count=0,
                        weight_value=receipt_item.weight_value,
                        weight_unit=receipt_item.weight_unit,
                    )
                    self.db.add(matched)
                    self.db.flush()
                    confidence = 1.0
                    print(f"Created new product: '{matched.name}' (id={matched.id}) in category '{cat.name}'")

            si = SubmissionItem(
                submission_id=submission.id,
                name=receipt_item.name,
                category=receipt_item.category,
                quantity=receipt_item.quantity,
                unit_price=receipt_item.unit_price,
                total_price=receipt_item.total_price,
                weight_value=receipt_item.weight_value,
                weight_unit=receipt_item.weight_unit,
                item_id=matched.id if matched else None,
            )
            # Store confidence for use in try_complete_submission
            si._match_confidence = confidence
            self.db.add(si)

        self.db.commit()
        self.db.refresh(submission)

        try_complete_submission(self.db, submission)
        self.db.refresh(submission)
        return submission

    async def process_receipt_image(
        self, image_data: bytes, mime_type: str = "image/jpeg", user_id: int | None = None
    ) -> Submission:
        """Extract receipt data from an image and create a submission."""
        receipt = await extract_receipt(image_data, mime_type)

        # Create receipt record
        receipt_record = None
        if user_id:
            receipt_record = ReceiptRecord(
                user_id=user_id,
                ocr_parsed_json=receipt.model_dump(),
                purchase_date=None,
                status="pending",
            )
            if receipt.date:
                try:
                    receipt_record.purchase_date = date.fromisoformat(receipt.date)
                except ValueError:
                    pass
            self.db.add(receipt_record)
            self.db.flush()

        submission = self._create_submission(
            receipt,
            user_id=user_id,
            receipt_id=receipt_record.id if receipt_record else None,
        )

        # Mark receipt as processed
        if receipt_record:
            receipt_record.status = "processed"
            receipt_record.store_location_id = submission.store_id
            self.db.commit()

        return submission

    def process_manual_receipt(self, receipt: ReceiptData, user_id: int | None = None) -> Submission:
        """Create a submission from manually submitted receipt data."""
        return self._create_submission(receipt, user_id=user_id)
