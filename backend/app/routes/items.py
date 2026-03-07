from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.category import Category
from app.models.grocery_item import GroceryItem
from app.schemas.items import CategoryOut, GroceryItemOut, PricePointOut
from app.services.price_service import get_price_history

router = APIRouter()


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.get("/items", response_model=list[GroceryItemOut])
def list_items(
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    sort: Optional[str] = Query(None, regex="^(price_asc|price_desc|change_asc|change_desc|name)$"),
    db: Session = Depends(get_db),
):
    q = db.query(GroceryItem)

    if search:
        q = q.filter(GroceryItem.name.ilike(f"%{search}%"))
    if category_id:
        q = q.filter(GroceryItem.category_id == category_id)

    if sort == "price_asc":
        q = q.order_by(GroceryItem.current_price.asc())
    elif sort == "price_desc":
        q = q.order_by(GroceryItem.current_price.desc())
    elif sort == "change_asc":
        q = q.order_by(GroceryItem.price_change_pct.asc())
    elif sort == "change_desc":
        q = q.order_by(GroceryItem.price_change_pct.desc())
    else:
        q = q.order_by(GroceryItem.name)

    items = q.all()
    result = []
    for item in items:
        out = GroceryItemOut.model_validate(item)
        if item.category:
            out.category_name = item.category.name
        result.append(out)
    return result


@router.get("/items/{item_id}", response_model=GroceryItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(GroceryItem).filter(GroceryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    out = GroceryItemOut.model_validate(item)
    if item.category:
        out.category_name = item.category.name
    return out


@router.get("/items/{item_id}/price-history", response_model=list[PricePointOut])
def item_price_history(
    item_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    item = db.query(GroceryItem).filter(GroceryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return get_price_history(db, item_id, days)
