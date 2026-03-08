"""
End-to-end test: insert a price-drop submission for every product,
run the aggregation cronjob, and verify price_by_hour reflects the drop.

Usage:
    docker-compose exec backend pytest tests/test_price_drop.py -v -s
"""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from unittest.mock import patch

from app.database import Base
from app.models import ProductItem, PriceByHour
from app.models.user import User
from app.models.submission import Submission
from app.models.submission_item import SubmissionItem
from app.jobs.price_aggregation import aggregate_hourly_prices

TEST_DB_URL = "postgresql://hackcanada:hackcanada@postgres:5432/hackcanada_db"
engine = create_engine(TEST_DB_URL)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

PRICE_DROP_PCT = 0.20  # 20% drop


def test_price_drop_all_products():
    db = TestSession()
    now = datetime.now(timezone.utc)
    hour_truncated = now.replace(minute=0, second=0, microsecond=0)

    # ── 1. Get all products and their current (latest) prices ──
    products = db.query(ProductItem).all()
    assert len(products) > 0, "No products in DB — run seed first"

    print(f"\n{'='*70}")
    print(f"  PRICE DROP TEST — {len(products)} products, {PRICE_DROP_PCT*100:.0f}% drop")
    print(f"{'='*70}")

    before_prices = {}
    for p in products:
        latest = (
            db.query(PriceByHour)
            .filter(PriceByHour.p_id == p.p_id)
            .order_by(PriceByHour.timestamp.desc())
            .first()
        )
        before_prices[p.p_id] = latest.price if latest else None

    print(f"\n  BEFORE (latest price_by_hour per product):")
    for p in products:
        print(f"    {p.name:<30} ${before_prices[p.p_id]:.2f}")

    # ── 2. Ensure test user exists ──
    user = db.query(User).filter(User.u_id == "test_drop_user").first()
    if not user:
        user = User(u_id="test_drop_user", name="Price Drop Tester")
        db.add(user)
        db.commit()

    # ── 3. Create a confirmed submission with dropped prices ──
    sub_id = f"drop_{uuid.uuid4().hex[:8]}"
    submission = Submission(
        sub_id=sub_id,
        u_id=user.u_id,
        is_confirmed=True,
        created_at=now - timedelta(minutes=5),  # 5 min ago (within the hour)
    )
    db.add(submission)
    db.flush()

    dropped_prices = {}
    for p in products:
        old_price = before_prices[p.p_id]
        if old_price is None:
            continue
        new_price = round(old_price * (1 - PRICE_DROP_PCT), 2)
        dropped_prices[p.p_id] = new_price

        db.add(SubmissionItem(
            sub_item_id=f"si_{uuid.uuid4().hex[:8]}",
            p_id=p.p_id,
            sub_id=sub_id,
            price=new_price,
        ))

    db.commit()

    print(f"\n  [INSERT] Submission {sub_id} (confirmed, {len(dropped_prices)} items)")
    print(f"  Submitted prices (20% drop):")
    for p in products:
        if p.p_id in dropped_prices:
            print(f"    {p.name:<30} ${before_prices[p.p_id]:.2f} -> ${dropped_prices[p.p_id]:.2f}")

    # ── 4. Delete any existing price_by_hour row for this hour so the job writes fresh ──
    db.query(PriceByHour).filter(PriceByHour.timestamp == hour_truncated).delete()
    db.commit()

    # ── 5. Run the aggregation cronjob ──
    print(f"\n  [RUN] aggregate_hourly_prices()  (hour bucket: {hour_truncated})")

    with patch("app.jobs.price_aggregation.SessionLocal", TestSession):
        aggregate_hourly_prices()

    # ── 6. Verify the new price_by_hour rows ──
    print(f"\n  AFTER (price_by_hour at {hour_truncated}):")
    all_pass = True
    for p in products:
        row = (
            db.query(PriceByHour)
            .filter(PriceByHour.p_id == p.p_id, PriceByHour.timestamp == hour_truncated)
            .first()
        )
        if row is None:
            print(f"    {p.name:<30} NO ROW — FAIL")
            all_pass = False
            continue

        expected = dropped_prices[p.p_id]
        status = "OK" if row.price == expected else "MISMATCH"
        if status == "MISMATCH":
            all_pass = False
        print(f"    {p.name:<30} ${row.price:.2f}  (expected ${expected:.2f})  [{status}]")

    print(f"\n  Latest price (what the frontend will show):")
    for p in products:
        latest = (
            db.query(PriceByHour)
            .filter(PriceByHour.p_id == p.p_id)
            .order_by(PriceByHour.timestamp.desc())
            .first()
        )
        old = before_prices[p.p_id]
        change = ((latest.price - old) / old) * 100 if old else 0
        print(f"    {p.name:<30} ${latest.price:.2f}  ({change:+.1f}%)")

    print(f"\n{'='*70}")

    # ── 7. Cleanup test submission ──
    db.query(SubmissionItem).filter(SubmissionItem.sub_id == sub_id).delete()
    db.query(Submission).filter(Submission.sub_id == sub_id).delete()
    db.query(User).filter(User.u_id == "test_drop_user").delete()
    db.commit()
    db.close()

    assert all_pass, "Some prices did not match expected values"
