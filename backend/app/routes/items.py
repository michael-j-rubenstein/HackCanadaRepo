from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.database import get_db
from app.models import ProductItem, Category, Brand, PriceByHour, CartItem, User

router = APIRouter()


class CategoryResponse(BaseModel):
    id: str
    name: str
    icon: Optional[str] = None

    class Config:
        from_attributes = True


class ItemResponse(BaseModel):
    id: str
    name: str
    brand: Optional[str] = None
    unit: str
    category_id: str
    category_name: Optional[str] = None
    current_price: Optional[float] = None
    price_change_pct: Optional[float] = None

    class Config:
        from_attributes = True


class PriceHistoryPoint(BaseModel):
    date: str
    avg_price: float


class CartItemResponse(BaseModel):
    id: str
    item_id: str
    item_name: Optional[str] = None


class CartItemCreate(BaseModel):
    item_id: str


class PinnedItemResponse(BaseModel):
    id: str
    item_id: str
    item_name: Optional[str] = None
    current_price: Optional[float] = None
    price_change_pct: Optional[float] = None


class PinnedItemCreate(BaseModel):
    item_id: str


# In-memory pins storage (since no pins table exists)
_user_pins: dict[str, set[str]] = {}


def get_current_price(db: Session, p_id: str) -> Optional[float]:
    """Get the most recent price for a product."""
    latest = db.query(PriceByHour).filter(
        PriceByHour.p_id == p_id
    ).order_by(PriceByHour.timestamp.desc()).first()
    return latest.price if latest else None


def get_price_change_pct(db: Session, p_id: str) -> Optional[float]:
    """Calculate price change percentage over last 7 days."""
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    prices = db.query(PriceByHour).filter(
        PriceByHour.p_id == p_id,
        PriceByHour.timestamp >= week_ago
    ).order_by(PriceByHour.timestamp).all()

    if len(prices) < 2:
        return None

    old_price = prices[0].price
    new_price = prices[-1].price

    if old_price == 0:
        return None

    return ((new_price - old_price) / old_price) * 100


@router.get("/categories", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return [
        CategoryResponse(id=c.c_id, name=c.name, icon=None)
        for c in categories
    ]


@router.get("/items", response_model=list[ItemResponse])
def get_items(
    search: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ProductItem)

    if search:
        query = query.filter(ProductItem.name.ilike(f"%{search}%"))

    if category_id:
        query = query.filter(ProductItem.c_id == category_id)

    products = query.all()

    result = []
    for p in products:
        current_price = get_current_price(db, p.p_id)
        price_change = get_price_change_pct(db, p.p_id)

        result.append(ItemResponse(
            id=p.p_id,
            name=p.name,
            brand=p.brand.name if p.brand else None,
            unit=p.category.unit if p.category else "",
            category_id=p.c_id,
            category_name=p.category.name if p.category else None,
            current_price=current_price,
            price_change_pct=price_change
        ))

    if sort == "price_asc":
        result.sort(key=lambda x: x.current_price or float('inf'))
    elif sort == "price_desc":
        result.sort(key=lambda x: x.current_price or 0, reverse=True)

    return result


@router.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: str, db: Session = Depends(get_db)):
    product = db.query(ProductItem).filter(ProductItem.p_id == item_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Item not found")

    current_price = get_current_price(db, product.p_id)
    price_change = get_price_change_pct(db, product.p_id)

    return ItemResponse(
        id=product.p_id,
        name=product.name,
        brand=product.brand.name if product.brand else None,
        unit=product.category.unit if product.category else "",
        category_id=product.c_id,
        category_name=product.category.name if product.category else None,
        current_price=current_price,
        price_change_pct=price_change
    )


@router.get("/items/{item_id}/price-history", response_model=list[PriceHistoryPoint])
def get_price_history(
    item_id: str,
    days: int = Query(30),
    db: Session = Depends(get_db)
):
    cutoff = datetime.utcnow() - timedelta(days=days)

    prices = db.query(
        func.date(PriceByHour.timestamp).label('date'),
        func.avg(PriceByHour.price).label('avg_price')
    ).filter(
        PriceByHour.p_id == item_id,
        PriceByHour.timestamp >= cutoff
    ).group_by(
        func.date(PriceByHour.timestamp)
    ).order_by(
        func.date(PriceByHour.timestamp)
    ).all()

    return [
        PriceHistoryPoint(date=str(p.date), avg_price=round(p.avg_price, 2))
        for p in prices
    ]


@router.get("/cart", response_model=list[CartItemResponse])
def get_cart(
    x_user_id: str = Header(..., alias="X-User-Id"),
    db: Session = Depends(get_db)
):
    cart_items = db.query(CartItem).filter(CartItem.u_id == x_user_id).all()
    return [
        CartItemResponse(
            id=f"{ci.u_id}_{ci.p_id}",
            item_id=ci.p_id,
            item_name=ci.product.name if ci.product else None
        )
        for ci in cart_items
    ]


@router.post("/cart", response_model=CartItemResponse)
def add_to_cart(
    body: CartItemCreate,
    x_user_id: str = Header(..., alias="X-User-Id"),
    db: Session = Depends(get_db)
):
    # Ensure user exists
    user = db.query(User).filter(User.u_id == x_user_id).first()
    if not user:
        user = User(u_id=x_user_id, name=x_user_id)
        db.add(user)
        db.commit()

    # Check if already in cart
    existing = db.query(CartItem).filter(
        CartItem.u_id == x_user_id,
        CartItem.p_id == body.item_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Item already in cart")

    cart_item = CartItem(u_id=x_user_id, p_id=body.item_id)
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    product = db.query(ProductItem).filter(ProductItem.p_id == body.item_id).first()

    return CartItemResponse(
        id=f"{cart_item.u_id}_{cart_item.p_id}",
        item_id=cart_item.p_id,
        item_name=product.name if product else None
    )


@router.delete("/cart/{item_id}")
def remove_from_cart(
    item_id: str,
    x_user_id: str = Header(..., alias="X-User-Id"),
    db: Session = Depends(get_db)
):
    cart_item = db.query(CartItem).filter(
        CartItem.u_id == x_user_id,
        CartItem.p_id == item_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not in cart")

    db.delete(cart_item)
    db.commit()
    return {"message": "Removed from cart"}


@router.get("/pins", response_model=list[PinnedItemResponse])
def get_pins(
    x_user_id: str = Header(..., alias="X-User-Id"),
    db: Session = Depends(get_db)
):
    user_pins = _user_pins.get(x_user_id, set())
    result = []

    for p_id in user_pins:
        product = db.query(ProductItem).filter(ProductItem.p_id == p_id).first()
        if product:
            current_price = get_current_price(db, p_id)
            price_change = get_price_change_pct(db, p_id)
            result.append(PinnedItemResponse(
                id=f"{x_user_id}_{p_id}",
                item_id=p_id,
                item_name=product.name,
                current_price=current_price,
                price_change_pct=price_change
            ))

    return result


@router.post("/pins", response_model=PinnedItemResponse)
def pin_item(
    body: PinnedItemCreate,
    x_user_id: str = Header(..., alias="X-User-Id"),
    db: Session = Depends(get_db)
):
    if x_user_id not in _user_pins:
        _user_pins[x_user_id] = set()

    _user_pins[x_user_id].add(body.item_id)

    product = db.query(ProductItem).filter(ProductItem.p_id == body.item_id).first()
    current_price = get_current_price(db, body.item_id) if product else None
    price_change = get_price_change_pct(db, body.item_id) if product else None

    return PinnedItemResponse(
        id=f"{x_user_id}_{body.item_id}",
        item_id=body.item_id,
        item_name=product.name if product else None,
        current_price=current_price,
        price_change_pct=price_change
    )


@router.delete("/pins/{item_id}")
def unpin_item(
    item_id: str,
    x_user_id: str = Header(..., alias="X-User-Id"),
):
    if x_user_id in _user_pins:
        _user_pins[x_user_id].discard(item_id)
    return {"message": "Unpinned"}
