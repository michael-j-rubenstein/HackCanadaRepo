from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.store import Store
from app.schemas.items import StoreOut
from app.services.geo import haversine_filter

router = APIRouter()


@router.get("/stores", response_model=list[StoreOut])
def list_stores(
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius_km: Optional[float] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Store)
    if lat is not None and lng is not None and radius_km is not None:
        q = haversine_filter(q, lat, lng, radius_km)
    return q.order_by(Store.name).all()
