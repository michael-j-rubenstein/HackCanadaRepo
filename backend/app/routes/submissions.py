from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.grocery_item import GroceryItem
from app.models.price_submission import PriceSubmission
from app.schemas.submissions import PriceSubmissionCreate, PriceSubmissionOut
from app.services.price_service import recalculate_current_price, check_alerts

router = APIRouter()


@router.post("/items/{item_id}/submit-price", response_model=PriceSubmissionOut)
def submit_price(
    item_id: int,
    data: PriceSubmissionCreate,
    db: Session = Depends(get_db),
):
    item = db.query(GroceryItem).filter(GroceryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    submission = PriceSubmission(
        item_id=item_id,
        price=data.price,
        store_name=data.store_name,
        date_observed=data.date_observed,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    recalculate_current_price(db, item_id)
    check_alerts(db, item_id)

    return submission
