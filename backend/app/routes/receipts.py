import re
import uuid
import base64
from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, File
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models import ProductItem, Submission, SubmissionItem, User, Category, Brand, Store
from app.models.receipt import ReceiptData, ReceiptItem
from app.clients.gemini import extract_receipt
from app.services.gemini import generate_structured_async
from google.genai import types

router = APIRouter(prefix="/receipts", tags=["receipts"])


class MatchedItem(BaseModel):
    receipt_item: ReceiptItem
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    confidence: float = 0.0
    is_auto_created: bool = False


class ScanResponse(BaseModel):
    store_name: Optional[str] = None
    date: Optional[str] = None
    matched_items: list[MatchedItem] = []
    unmatched_items: list[ReceiptItem] = []
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None


class SubmitItem(BaseModel):
    product_id: str
    price: float


class SubmitRequest(BaseModel):
    store_name: Optional[str] = None
    date: Optional[str] = None
    items: list[SubmitItem]


class SubmitResponse(BaseModel):
    submission_id: str
    items_count: int


class ProductMatch(BaseModel):
    receipt_item_name: str
    product_id: Optional[str] = None
    confidence: float = 0.0


class MatchResult(BaseModel):
    matches: list[ProductMatch]


class ScanBase64Request(BaseModel):
    image_base64: str
    mime_type: str = "image/jpeg"


def slugify(text: str) -> str:
    """Convert text to a slug: 'Green Peppers' -> 'green_peppers'."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


CATEGORY_UNIT_DEFAULTS = {
    "dairy": "L",
    "produce": "kg",
    "meat": "kg",
    "eggs": "unit",
    "bakery": "unit",
    "frozen": "unit",
    "snacks": "unit",
    "grocery": "unit",
}


def get_or_create_category(name: str, weight_unit: Optional[str], db: Session) -> Category:
    """Find or create a category by name (case-insensitive)."""
    cat = db.query(Category).filter(func.lower(Category.name) == name.lower()).first()
    if cat:
        return cat

    # Infer unit from weight_unit or category defaults
    if weight_unit and weight_unit in ("g", "kg", "lb", "oz"):
        unit = "kg"
    elif weight_unit and weight_unit in ("ml", "L"):
        unit = "L"
    else:
        unit = CATEGORY_UNIT_DEFAULTS.get(name.lower(), "unit")

    cat = Category(c_id=f"cat_{slugify(name)}", name=name.capitalize(), unit=unit)
    db.add(cat)
    db.flush()
    return cat


def get_or_create_store(store_name: Optional[str], db: Session) -> Store:
    """Find or create a store by name (case-insensitive). Falls back to first existing store."""
    if store_name:
        store = db.query(Store).filter(func.lower(Store.name) == store_name.lower()).first()
        if store:
            return store
        store = Store(store_id=f"store_{slugify(store_name)}", name=store_name)
        db.add(store)
        db.flush()
        return store

    # Fallback to first existing store
    store = db.query(Store).first()
    if store:
        return store
    store = Store(store_id="store_unknown", name="Unknown Store")
    db.add(store)
    db.flush()
    return store


def find_brand(item_name: str, db: Session) -> Brand:
    """Check if any existing brand name appears as a substring in the item name."""
    brands = db.query(Brand).all()
    item_lower = item_name.lower()
    for brand in brands:
        if brand.name.lower() != "generic" and brand.name.lower() in item_lower:
            return brand
    # Fallback to brand_generic
    generic = db.query(Brand).filter(Brand.brand_id == "brand_generic").first()
    if generic:
        return generic
    generic = Brand(brand_id="brand_generic", name="Generic")
    db.add(generic)
    db.flush()
    return generic


def auto_create_products_for_unmatched(
    unmatched_items: list[ReceiptItem],
    store_name: Optional[str],
    db: Session,
) -> list[MatchedItem]:
    """Auto-create ProductItem records for unmatched receipt items."""
    if not unmatched_items:
        return []

    store = get_or_create_store(store_name, db)
    results = []

    for item in unmatched_items:
        category = get_or_create_category(item.category or "Grocery", item.weight_unit, db)
        brand = find_brand(item.name, db)

        p_id = f"prod_{slugify(item.name)}_{slugify(store.name)}"

        existing = db.query(ProductItem).filter(ProductItem.p_id == p_id).first()
        if not existing:
            product = ProductItem(
                p_id=p_id,
                name=item.name,
                c_id=category.c_id,
                brand_id=brand.brand_id,
                store_id=store.store_id,
            )
            db.add(product)
            db.flush()
        else:
            product = existing

        results.append(MatchedItem(
            receipt_item=item,
            product_id=product.p_id,
            product_name=product.name,
            confidence=1.0,
            is_auto_created=True,
        ))

    return results


MATCH_PROMPT = """You are a product matching assistant. Given a list of receipt item names and a list of available products, match each receipt item to the most similar product.

Receipt items to match:
{receipt_items}

Available products (id: name):
{products}

For each receipt item, find the best matching product. Consider:
- Similar names (e.g., "GRN PEPPERS" matches "Green Peppers")
- Same category of food
- Common abbreviations

Return a match for EVERY receipt item. If no good match exists, set product_id to null and confidence to 0.
Confidence should be 0.0-1.0 where 1.0 is an exact match."""


async def match_items_to_products(
    receipt_items: list[ReceiptItem],
    db: Session
) -> tuple[list[MatchedItem], list[ReceiptItem]]:
    """Match receipt items to products in the database using Gemini."""
    if not receipt_items:
        return [], []

    products = db.query(ProductItem).all()
    if not products:
        return [], receipt_items

    product_list = "\n".join([f"{p.p_id}: {p.name}" for p in products])
    receipt_list = "\n".join([f"- {item.name}" for item in receipt_items])

    prompt = MATCH_PROMPT.format(
        receipt_items=receipt_list,
        products=product_list
    )

    contents = [types.Content(parts=[types.Part.from_text(text=prompt)])]

    try:
        text = await generate_structured_async(
            contents=contents,
            response_schema=MatchResult.model_json_schema(),
        )
        result = MatchResult.model_validate_json(text)
    except Exception as e:
        print(f"Error matching items: {e}")
        return [], receipt_items

    product_map = {p.p_id: p.name for p in products}
    matched = []
    unmatched = []

    item_map = {item.name.lower(): item for item in receipt_items}

    for match in result.matches:
        receipt_item = item_map.get(match.receipt_item_name.lower())
        if not receipt_item:
            for item in receipt_items:
                if item.name.lower() in match.receipt_item_name.lower() or match.receipt_item_name.lower() in item.name.lower():
                    receipt_item = item
                    break

        if not receipt_item:
            continue

        if match.product_id and match.confidence >= 0.5:
            matched.append(MatchedItem(
                receipt_item=receipt_item,
                product_id=match.product_id,
                product_name=product_map.get(match.product_id),
                confidence=match.confidence
            ))
        else:
            unmatched.append(receipt_item)

    matched_names = {m.receipt_item.name for m in matched}
    for item in receipt_items:
        if item.name not in matched_names and item not in unmatched:
            unmatched.append(item)

    return matched, unmatched


@router.post("/scan", response_model=ScanResponse)
async def scan_receipt(
    file: UploadFile = File(...),
    x_user_id: str = Header(..., alias="X-User-Id"),
    db: Session = Depends(get_db)
):
    """Upload a receipt image, extract data with OCR, and match to products."""
    content_type = file.content_type or "image/jpeg"
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_data = await file.read()

    try:
        receipt_data = await extract_receipt(image_data, content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

    matched, unmatched = await match_items_to_products(receipt_data.items, db)

    auto_created = auto_create_products_for_unmatched(unmatched, receipt_data.store_name, db)
    matched.extend(auto_created)
    db.commit()

    return ScanResponse(
        store_name=receipt_data.store_name,
        date=receipt_data.date,
        matched_items=matched,
        unmatched_items=[],
        subtotal=receipt_data.subtotal,
        tax=receipt_data.tax,
        total=receipt_data.total
    )


@router.post("/scan-base64", response_model=ScanResponse)
async def scan_receipt_base64(
    body: ScanBase64Request,
    x_user_id: str = Header(..., alias="X-User-Id"),
    db: Session = Depends(get_db)
):
    """Upload a receipt image as base64, extract data with OCR, and match to products."""
    if not body.mime_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        image_data = base64.b64decode(body.image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 data")

    try:
        receipt_data = await extract_receipt(image_data, body.mime_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

    matched, unmatched = await match_items_to_products(receipt_data.items, db)

    auto_created = auto_create_products_for_unmatched(unmatched, receipt_data.store_name, db)
    matched.extend(auto_created)
    db.commit()

    return ScanResponse(
        store_name=receipt_data.store_name,
        date=receipt_data.date,
        matched_items=matched,
        unmatched_items=[],
        subtotal=receipt_data.subtotal,
        tax=receipt_data.tax,
        total=receipt_data.total
    )


@router.post("/submit", response_model=SubmitResponse)
async def submit_receipt(
    body: SubmitRequest,
    x_user_id: str = Header(..., alias="X-User-Id"),
    db: Session = Depends(get_db)
):
    """Confirm and save receipt data to submissions and submission_items tables."""
    user = db.query(User).filter(User.u_id == x_user_id).first()
    if not user:
        user = User(u_id=x_user_id, name=x_user_id)
        db.add(user)
        db.commit()

    sub_id = str(uuid.uuid4())
    submission = Submission(
        sub_id=sub_id,
        u_id=x_user_id,
        receipt={
            "store_name": body.store_name,
            "date": body.date,
            "items_count": len(body.items)
        },
        is_confirmed=True
    )
    db.add(submission)

    for item in body.items:
        product = db.query(ProductItem).filter(ProductItem.p_id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")

        sub_item = SubmissionItem(
            sub_item_id=str(uuid.uuid4()),
            p_id=item.product_id,
            sub_id=sub_id,
            price=item.price
        )
        db.add(sub_item)

    db.commit()

    return SubmitResponse(
        submission_id=sub_id,
        items_count=len(body.items)
    )
