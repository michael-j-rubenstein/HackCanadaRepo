from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.pinned_item import PinnedItem
from app.models.grocery_item import GroceryItem
from app.schemas.pins import PinnedItemCreate, PinnedItemOut

router = APIRouter()


@router.get("/pins", response_model=list[PinnedItemOut])
def list_pins(db: Session = Depends(get_db)):
    pins = db.query(PinnedItem).order_by(PinnedItem.created_at.desc()).all()
    result = []
    for pin in pins:
        out = PinnedItemOut.model_validate(pin)
        if pin.item:
            out.item_name = pin.item.name
            out.current_price = pin.item.current_price
            out.price_change_pct = pin.item.price_change_pct
        result.append(out)
    return result


@router.post("/pins", response_model=PinnedItemOut, status_code=200)
def pin_item(data: PinnedItemCreate, db: Session = Depends(get_db)):
    item = db.query(GroceryItem).filter(GroceryItem.id == data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    existing = db.query(PinnedItem).filter(PinnedItem.item_id == data.item_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Item already pinned")

    pin = PinnedItem(item_id=data.item_id)
    db.add(pin)
    db.commit()
    db.refresh(pin)

    out = PinnedItemOut.model_validate(pin)
    out.item_name = item.name
    out.current_price = item.current_price
    out.price_change_pct = item.price_change_pct
    return out


@router.delete("/pins/{item_id}")
def unpin_item(item_id: int, db: Session = Depends(get_db)):
    pin = db.query(PinnedItem).filter(PinnedItem.item_id == item_id).first()
    if not pin:
        raise HTTPException(status_code=404, detail="Item not pinned")
    db.delete(pin)
    db.commit()
    return {"ok": True}
