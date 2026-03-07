from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.daos.price_dao import PriceDAO

router = APIRouter()


class ScrapedProduct(BaseModel):
    name: str
    brand: Optional[str] = None
    price: float
    unitPrice: Optional[float] = None
    unitPriceUnit: Optional[str] = None
    packageSize: Optional[str] = None
    category: Optional[str] = None
    storeId: Optional[int] = None
    storeBanner: Optional[str] = None


class IngestRequest(BaseModel):
    items: list[ScrapedProduct]


@router.post("/internal/baseline-ingest")
def baseline_ingest(
    data: IngestRequest,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
):
    if x_api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")

    dao = PriceDAO(db)
    created = 0

    for sp in data.items:
        matched, confidence = dao.find_item(sp.name, sp.category)

        if not matched:
            continue

        store_id = sp.storeId
        if not store_id and sp.storeBanner:
            store = dao.get_or_create_store(sp.storeBanner)
            store_id = store.id

        if not store_id:
            continue

        dao.create_price_submission(
            item_id=matched.id,
            price=sp.price,
            store_id=store_id,
            date_observed=date.today(),
            report_type="baseline",
            source="realdataapi",
            confidence=confidence,
            is_verified=True,
        )
        created += 1

    dao.commit()
    return {"ingested": created, "total": len(data.items)}
