from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rate_limit import check_submission_rate
from app.models.grocery_item import GroceryItem
from app.models.receipt import ReceiptData
from app.models.submission import Submission, SubmissionItem
from app.models.user import User
from app.daos.price_dao import PriceDAO
from app.schemas.submissions import (
    SubmissionOut,
    SubmissionItemOut,
    SubmissionUpdate,
)
from app.services.price_service import PriceService, try_complete_submission

router = APIRouter()

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _build_submission_out(submission: Submission) -> SubmissionOut:
    items = []
    for si in submission.items:
        item_out = SubmissionItemOut.model_validate(si)
        item_out.is_valid = si.item_id is not None
        item_out.item_name = si.item.name if si.item else None
        items.append(item_out)
    out = SubmissionOut.model_validate(submission)
    out.items = items
    return out


@router.post(
    "/submissions/scan",
    response_model=SubmissionOut,
    status_code=status.HTTP_202_ACCEPTED,
)
async def scan_receipt(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_submission_rate(user.id, db)

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: {', '.join(ALLOWED_MIME_TYPES)}",
        )

    image_data = await file.read()
    if not image_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    service = PriceService(db)
    submission = await service.process_receipt_image(image_data, file.content_type, user_id=user.id)
    return _build_submission_out(submission)


@router.post(
    "/submissions/manual",
    response_model=SubmissionOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def submit_manual_receipt(
    receipt: ReceiptData,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_submission_rate(user.id, db)

    if not receipt.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Receipt must contain at least one item",
        )

    service = PriceService(db)
    submission = service.process_manual_receipt(receipt, user_id=user.id)
    return _build_submission_out(submission)


@router.get("/submissions", response_model=list[SubmissionOut])
def list_submissions(
    status: str | None = Query(default=None, pattern="^(pending|completed)$"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Submission).filter(Submission.user_id == user.id)
    if status:
        query = query.filter(Submission.status == status)
    subs = query.order_by(Submission.created_at.desc()).all()
    return [_build_submission_out(s) for s in subs]


@router.get("/submissions/{submission_id}", response_model=SubmissionOut)
def get_submission(
    submission_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submission = (
        db.query(Submission)
        .filter(Submission.id == submission_id, Submission.user_id == user.id)
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return _build_submission_out(submission)


@router.patch("/submissions/{submission_id}", response_model=SubmissionOut)
def update_submission(
    submission_id: int,
    update: SubmissionUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submission = (
        db.query(Submission)
        .filter(Submission.id == submission_id, Submission.user_id == user.id)
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if submission.status == "completed":
        raise HTTPException(status_code=400, detail="Cannot edit a completed submission")

    if update.store_name is not None:
        submission.store_name = update.store_name
    if update.date_observed is not None:
        submission.date_observed = update.date_observed

    db.query(SubmissionItem).filter(SubmissionItem.submission_id == submission_id).delete()
    db.flush()

    dao = PriceDAO(db)
    for item_in in update.items:
        if item_in.item_id is not None:
            gi = db.query(GroceryItem).filter(GroceryItem.id == item_in.item_id).first()
            if not gi:
                raise HTTPException(status_code=400, detail=f"Grocery item {item_in.item_id} not found")
            matched_id = item_in.item_id
        else:
            matched, _ = dao.find_item(item_in.name, item_in.category)
            matched_id = matched.id if matched else None

        si = SubmissionItem(
            submission_id=submission_id,
            name=item_in.name,
            category=item_in.category,
            quantity=item_in.quantity,
            unit_price=item_in.unit_price,
            total_price=item_in.total_price,
            weight_value=item_in.weight_value,
            weight_unit=item_in.weight_unit,
            item_id=matched_id,
        )
        db.add(si)

    db.commit()
    db.refresh(submission)

    try_complete_submission(db, submission)
    db.refresh(submission)

    return _build_submission_out(submission)


@router.delete("/submissions/{submission_id}", status_code=204)
def delete_submission(
    submission_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submission = (
        db.query(Submission)
        .filter(Submission.id == submission_id, Submission.user_id == user.id)
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if submission.status == "completed":
        raise HTTPException(status_code=400, detail="Cannot delete a completed submission")

    db.delete(submission)
    db.commit()
