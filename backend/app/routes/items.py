from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.category import Category
from app.models.grocery_item import GroceryItem
from app.models.price_submission import PriceSubmission
from app.models.store import Store
from app.schemas.items import CategoryOut, GroceryItemOut, PricePointOut, StorePriceOut
from app.services.geo import get_store_ids_in_radius
from app.services.price_service import get_latest_price, get_price_history, get_store_prices
from app.services.unit_conversion import compute_price_per_100g

router = APIRouter()


def _enrich_item(item: GroceryItem, db: Session) -> GroceryItemOut:
    out = GroceryItemOut.model_validate(item)
    if item.category:
        out.category_name = item.category.name
    current_price = get_latest_price(db, item.id)
    out.current_price = current_price
    if current_price and item.weight_value and item.weight_unit:
        out.price_per_100g = compute_price_per_100g(
            current_price, item.weight_value, item.weight_unit
        )
    return out


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.get("/items", response_model=list[GroceryItemOut])
def list_items(
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    store_id: Optional[int] = Query(None),
    sort_by: Optional[str] = Query("name", regex="^(name|price)$"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    include_new: bool = Query(False),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius_km: Optional[float] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(GroceryItem)

    if not include_new:
        q = q.filter(GroceryItem.is_new == False)

    if search:
        q = q.filter(GroceryItem.name.ilike(f"%{search}%"))
    if category_id:
        q = q.filter(GroceryItem.category_id == category_id)

    # Radius filtering: only show items with prices at stores within radius
    store_ids = None
    if lat is not None and lng is not None and radius_km is not None:
        store_ids = get_store_ids_in_radius(db, lat, lng, radius_km)

    if store_id:
        q = q.filter(
            GroceryItem.id.in_(
                db.query(PriceSubmission.item_id)
                .filter(PriceSubmission.store_id == store_id)
                .distinct()
            )
        )
    elif store_ids is not None:
        q = q.filter(
            GroceryItem.id.in_(
                db.query(PriceSubmission.item_id)
                .filter(PriceSubmission.store_id.in_(store_ids))
                .distinct()
            )
        )

    items = [_enrich_item(item, db) for item in q.all()]

    if sort_by == "price":
        items.sort(
            key=lambda x: (x.current_price is None, x.current_price or 0),
            reverse=(sort_order == "desc"),
        )
    else:
        items.sort(key=lambda x: x.name, reverse=(sort_order == "desc"))

    return items


@router.get("/items/{item_id}", response_model=GroceryItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(GroceryItem).filter(GroceryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return _enrich_item(item, db)


@router.get("/items/{item_id}/price-history", response_model=list[PricePointOut])
def item_price_history(
    item_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius_km: Optional[float] = Query(None),
    db: Session = Depends(get_db),
):
    item = db.query(GroceryItem).filter(GroceryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return get_price_history(db, item_id, start_date, end_date, lat=lat, lng=lng, radius_km=radius_km)


@router.get("/items/{item_id}/store-prices", response_model=list[StorePriceOut])
def item_store_prices(
    item_id: int,
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius_km: Optional[float] = Query(None),
    db: Session = Depends(get_db),
):
    item = db.query(GroceryItem).filter(GroceryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return get_store_prices(db, item_id, lat=lat, lng=lng, radius_km=radius_km)


@router.get("/price-history/{scope_type}/{scope_id}")
def scoped_price_history(
    scope_type: str,
    scope_id: int,
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    bucket: str = Query("day", regex="^(day|week|month)$"),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius_km: Optional[float] = Query(None),
    db: Session = Depends(get_db),
):
    if scope_type not in ("product", "category"):
        raise HTTPException(status_code=400, detail="scope_type must be 'product' or 'category'")

    # Parse period
    period_days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}[period]
    start = date.today() - timedelta(days=period_days)

    store_ids = None
    if lat is not None and lng is not None and radius_km is not None:
        store_ids = get_store_ids_in_radius(db, lat, lng, radius_km)

    q = db.query(
        PriceSubmission.date_observed,
        sa_func.avg(PriceSubmission.price).label("avg_price"),
        sa_func.min(PriceSubmission.price).label("min_price"),
        sa_func.max(PriceSubmission.price).label("max_price"),
        sa_func.count(PriceSubmission.id).label("report_count"),
    ).filter(
        PriceSubmission.is_outlier == False,
        PriceSubmission.date_observed >= start,
    )

    if scope_type == "product":
        q = q.filter(PriceSubmission.item_id == scope_id)
    else:
        q = q.join(GroceryItem).filter(GroceryItem.category_id == scope_id)

    if store_ids is not None:
        q = q.filter(PriceSubmission.store_id.in_(store_ids))

    rows = q.group_by(PriceSubmission.date_observed).order_by(PriceSubmission.date_observed).all()

    series = [
        {
            "date": str(r.date_observed),
            "avg_price": round(r.avg_price, 2),
            "min_price": round(r.min_price, 2),
            "max_price": round(r.max_price, 2),
            "report_count": r.report_count,
        }
        for r in rows
    ]

    current_price = series[-1]["avg_price"] if series else None
    first_price = series[0]["avg_price"] if series else None
    price_change_pct = (
        round((current_price - first_price) / first_price * 100, 2)
        if current_price and first_price and first_price != 0
        else None
    )
    all_time_low = min(r["min_price"] for r in series) if series else None
    all_time_high = max(r["max_price"] for r in series) if series else None

    return {
        "scope_type": scope_type,
        "scope_id": scope_id,
        "period": period,
        "series": series,
        "current_price": current_price,
        "price_change_pct": price_change_pct,
        "all_time_low": all_time_low,
        "all_time_high": all_time_high,
    }


@router.get("/products/{product_id}/store-comparison")
def store_comparison(
    product_id: int,
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius_km: Optional[float] = Query(None),
    db: Session = Depends(get_db),
):
    item = db.query(GroceryItem).filter(GroceryItem.id == product_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")

    store_ids = None
    if lat is not None and lng is not None and radius_km is not None:
        store_ids = get_store_ids_in_radius(db, lat, lng, radius_km)

    from app.daos.price_dao import PriceDAO
    dao = PriceDAO(db)
    latest = dao.get_latest_prices_by_store(product_id, store_ids=store_ids)

    cutoff = date.today() - timedelta(days=30)
    results = []
    for ps in latest:
        avg_30d_row = (
            db.query(sa_func.avg(PriceSubmission.price))
            .filter(
                PriceSubmission.item_id == product_id,
                PriceSubmission.store_id == ps.store_id,
                PriceSubmission.date_observed >= cutoff,
                PriceSubmission.is_outlier == False,
            )
            .scalar()
        )
        report_count = (
            db.query(sa_func.count(PriceSubmission.id))
            .filter(
                PriceSubmission.item_id == product_id,
                PriceSubmission.store_id == ps.store_id,
                PriceSubmission.date_observed >= cutoff,
                PriceSubmission.is_outlier == False,
            )
            .scalar()
        )
        pp100g = ps.price_per_100g or compute_price_per_100g(
            ps.price, item.weight_value, item.weight_unit
        )
        results.append({
            "store_id": ps.store_id,
            "store_name": ps.store.name,
            "latest_price": ps.price,
            "avg_30d": round(avg_30d_row, 2) if avg_30d_row else None,
            "price_per_100g": pp100g,
            "report_count": report_count or 0,
            "date_observed": str(ps.date_observed),
        })

    results.sort(key=lambda x: x["latest_price"])
    return {"product_id": product_id, "product_name": item.name, "stores": results}
