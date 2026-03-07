from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.shopping_cart_item import ShoppingCartItem
from app.models.grocery_item import GroceryItem
from app.schemas.cart import ShoppingCartItemCreate, ShoppingCartItemOut

router = APIRouter()


@router.get("/cart", response_model=list[ShoppingCartItemOut])
def list_cart(db: Session = Depends(get_db)):
    cart_items = db.query(ShoppingCartItem).order_by(ShoppingCartItem.created_at.desc()).all()
    result = []
    for ci in cart_items:
        out = ShoppingCartItemOut.model_validate(ci)
        if ci.item:
            out.item_name = ci.item.name
        result.append(out)
    return result


@router.post("/cart", response_model=ShoppingCartItemOut, status_code=200)
def add_to_cart(data: ShoppingCartItemCreate, db: Session = Depends(get_db)):
    item = db.query(GroceryItem).filter(GroceryItem.id == data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    existing = db.query(ShoppingCartItem).filter(ShoppingCartItem.item_id == data.item_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Item already in cart")

    cart_item = ShoppingCartItem(item_id=data.item_id)
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    out = ShoppingCartItemOut.model_validate(cart_item)
    out.item_name = item.name
    return out


@router.delete("/cart/{item_id}")
def remove_from_cart(item_id: int, db: Session = Depends(get_db)):
    cart_item = db.query(ShoppingCartItem).filter(ShoppingCartItem.item_id == item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    db.delete(cart_item)
    db.commit()
    return {"ok": True}
