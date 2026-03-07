from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.price_alert import PriceAlert
from app.models.grocery_item import GroceryItem
from app.schemas.alerts import PriceAlertCreate, PriceAlertOut

router = APIRouter()


@router.get("/alerts", response_model=list[PriceAlertOut])
def list_alerts(db: Session = Depends(get_db)):
    alerts = db.query(PriceAlert).order_by(PriceAlert.created_at.desc()).all()
    result = []
    for alert in alerts:
        out = PriceAlertOut.model_validate(alert)
        if alert.item:
            out.item_name = alert.item.name
        result.append(out)
    return result


@router.post("/alerts", response_model=PriceAlertOut)
def create_alert(data: PriceAlertCreate, db: Session = Depends(get_db)):
    item = db.query(GroceryItem).filter(GroceryItem.id == data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    alert = PriceAlert(item_id=data.item_id, target_price=data.target_price)
    db.add(alert)
    db.commit()
    db.refresh(alert)

    out = PriceAlertOut.model_validate(alert)
    out.item_name = item.name
    return out


@router.delete("/alerts/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
    return {"ok": True}
