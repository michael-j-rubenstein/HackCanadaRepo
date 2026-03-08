"""Tests for the hourly price aggregation job.

Runs against the PostgreSQL database exposed at localhost:5433 via docker-compose.
"""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.category import Category
from app.models.brand import Brand
from app.models.store import Store
from app.models.product_item import ProductItem
from app.models.submission import Submission
from app.models.submission_item import SubmissionItem
from app.models.price_by_hour import PriceByHour
from app.jobs.price_aggregation import aggregate_hourly_prices

TEST_DB_URL = "postgresql://hackcanada:hackcanada@localhost:5433/hackcanada_db"

engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _uid():
    return str(uuid.uuid4())[:8]


@pytest.fixture(autouse=True)
def _cleanup(db):
    """Delete test data after each test (reverse order for FK constraints)."""
    yield
    db.query(PriceByHour).delete()
    db.query(SubmissionItem).delete()
    db.query(Submission).delete()
    db.query(ProductItem).filter(ProductItem.p_id.like("test_%")).delete()
    db.query(User).filter(User.u_id == "test_user").delete()
    db.query(Store).filter(Store.store_id == "test_store").delete()
    db.query(Brand).filter(Brand.brand_id == "test_brand").delete()
    db.query(Category).filter(Category.c_id == "test_cat").delete()
    db.commit()


@pytest.fixture
def db():
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def ref_data(db):
    """Shared reference data: category, brand, store, user."""
    cat = Category(c_id="test_cat", name="TestCategory", unit="kg")
    brand = Brand(brand_id="test_brand", name="TestBrand")
    store = Store(store_id="test_store", name="TestStore")
    user = User(u_id="test_user", name="Test User")
    db.add_all([cat, brand, store, user])
    db.commit()
    return cat, brand, store, user


def add_product(db, name, cat, brand, store):
    p_id = f"test_{name}"
    product = ProductItem(
        p_id=p_id, name=name,
        c_id=cat.c_id, brand_id=brand.brand_id, store_id=store.store_id,
    )
    db.add(product)
    db.commit()
    return product


def add_submission(db, user, items_with_prices, confirmed=True, created_at=None):
    """Create a submission with given items. items_with_prices: [(product, price), ...]"""
    sub_id = _uid()
    sub = Submission(
        sub_id=sub_id,
        u_id=user.u_id,
        is_confirmed=confirmed,
        created_at=created_at or datetime.now(timezone.utc),
    )
    db.add(sub)
    db.flush()

    for product, price in items_with_prices:
        db.add(SubmissionItem(
            sub_item_id=_uid(),
            p_id=product.p_id,
            sub_id=sub_id,
            price=price,
        ))
    db.commit()
    return sub


# ── Tests ────────────────────────────────────────────────────────────────


@patch("app.jobs.price_aggregation.SessionLocal", TestingSessionLocal)
def test_basic_aggregation(db, ref_data):
    """Submissions in the last hour produce correct average in price_by_hour."""
    cat, brand, store, user = ref_data
    milk = add_product(db, "milk", cat, brand, store)

    now = datetime.now(timezone.utc)
    sub1 = add_submission(db, user, [(milk, 3.00)], created_at=now - timedelta(minutes=30))
    sub2 = add_submission(db, user, [(milk, 5.00)], created_at=now - timedelta(minutes=10))

    print(f"\n  [INSERT] Product: milk (p_id={milk.p_id})")
    print(f"  [INSERT] Submission 1: milk=$3.00, created_at={sub1.created_at}")
    print(f"  [INSERT] Submission 2: milk=$5.00, created_at={sub2.created_at}")
    print(f"  [RUN]    aggregate_hourly_prices()")

    aggregate_hourly_prices()

    rows = db.query(PriceByHour).filter(PriceByHour.p_id == milk.p_id).all()
    print(f"  [RESULT] PriceByHour rows: {len(rows)}")
    print(f"  [RESULT] Computed avg price: ${rows[0].price:.2f} (expected $4.00 = avg(3.00, 5.00))")
    print(f"  [RESULT] Timestamp bucket: {rows[0].timestamp}")

    assert len(rows) == 1
    assert rows[0].price == 4.00  # avg(3, 5)

    hour_truncated = now.replace(minute=0, second=0, microsecond=0)
    # Compare without tzinfo discrepancies — both should represent the same hour
    assert rows[0].timestamp.replace(tzinfo=None) == hour_truncated.replace(tzinfo=None)


@patch("app.jobs.price_aggregation.SessionLocal", TestingSessionLocal)
def test_unconfirmed_submissions_excluded(db, ref_data):
    """Unconfirmed submissions are not included in the average."""
    cat, brand, store, user = ref_data
    eggs = add_product(db, "eggs", cat, brand, store)

    now = datetime.now(timezone.utc)
    sub1 = add_submission(db, user, [(eggs, 2.00)], confirmed=True, created_at=now - timedelta(minutes=20))
    sub2 = add_submission(db, user, [(eggs, 100.00)], confirmed=False, created_at=now - timedelta(minutes=10))

    print(f"\n  [INSERT] Product: eggs (p_id={eggs.p_id})")
    print(f"  [INSERT] Submission 1 (confirmed):   eggs=$2.00,   created_at={sub1.created_at}")
    print(f"  [INSERT] Submission 2 (unconfirmed): eggs=$100.00, created_at={sub2.created_at}")
    print(f"  [RUN]    aggregate_hourly_prices()")

    aggregate_hourly_prices()

    rows = db.query(PriceByHour).filter(PriceByHour.p_id == eggs.p_id).all()
    print(f"  [RESULT] PriceByHour rows: {len(rows)}")
    print(f"  [RESULT] Computed avg price: ${rows[0].price:.2f} (expected $2.00 — unconfirmed $100 excluded)")

    assert len(rows) == 1
    assert rows[0].price == 2.00


@patch("app.jobs.price_aggregation.SessionLocal", TestingSessionLocal)
def test_old_submissions_excluded(db, ref_data):
    """Submissions older than 1 hour are not aggregated."""
    cat, brand, store, user = ref_data
    bread = add_product(db, "bread", cat, brand, store)

    old_time = datetime.now(timezone.utc) - timedelta(hours=2)
    sub1 = add_submission(db, user, [(bread, 5.00)], created_at=old_time)

    print(f"\n  [INSERT] Product: bread (p_id={bread.p_id})")
    print(f"  [INSERT] Submission 1: bread=$5.00, created_at={sub1.created_at} (2 hours ago)")
    print(f"  [RUN]    aggregate_hourly_prices()")

    aggregate_hourly_prices()

    rows = db.query(PriceByHour).filter(PriceByHour.p_id == bread.p_id).all()
    print(f"  [RESULT] PriceByHour rows: {len(rows)} (expected 0 — submission too old)")

    assert len(rows) == 0


@patch("app.jobs.price_aggregation.SessionLocal", TestingSessionLocal)
def test_multiple_products(db, ref_data):
    """Each product gets its own aggregated row."""
    cat, brand, store, user = ref_data
    apple = add_product(db, "apple", cat, brand, store)
    banana = add_product(db, "banana", cat, brand, store)

    now = datetime.now(timezone.utc)
    sub1 = add_submission(db, user, [(apple, 1.50), (banana, 0.80)], created_at=now - timedelta(minutes=15))
    sub2 = add_submission(db, user, [(apple, 2.50), (banana, 1.20)], created_at=now - timedelta(minutes=5))

    print(f"\n  [INSERT] Product: apple (p_id={apple.p_id})")
    print(f"  [INSERT] Product: banana (p_id={banana.p_id})")
    print(f"  [INSERT] Submission 1: apple=$1.50, banana=$0.80, created_at={sub1.created_at}")
    print(f"  [INSERT] Submission 2: apple=$2.50, banana=$1.20, created_at={sub2.created_at}")
    print(f"  [RUN]    aggregate_hourly_prices()")

    aggregate_hourly_prices()

    rows = {r.p_id: r.price for r in db.query(PriceByHour).filter(
        PriceByHour.p_id.in_([apple.p_id, banana.p_id])
    ).all()}
    print(f"  [RESULT] PriceByHour rows: {len(rows)}")
    print(f"  [RESULT] apple avg: ${rows[apple.p_id]:.2f} (expected $2.00 = avg(1.50, 2.50))")
    print(f"  [RESULT] banana avg: ${rows[banana.p_id]:.2f} (expected $1.00 = avg(0.80, 1.20))")

    assert len(rows) == 2
    assert rows[apple.p_id] == 2.00   # avg(1.5, 2.5)
    assert rows[banana.p_id] == 1.00  # avg(0.8, 1.2)


@patch("app.jobs.price_aggregation.SessionLocal", TestingSessionLocal)
def test_duplicate_run_skips_existing(db, ref_data):
    """Running the job twice in the same hour doesn't overwrite existing rows."""
    cat, brand, store, user = ref_data
    juice = add_product(db, "juice", cat, brand, store)

    now = datetime.now(timezone.utc)
    sub1 = add_submission(db, user, [(juice, 3.00)], created_at=now - timedelta(minutes=30))

    print(f"\n  [INSERT] Product: juice (p_id={juice.p_id})")
    print(f"  [INSERT] Submission 1: juice=$3.00, created_at={sub1.created_at}")
    print(f"  [RUN]    aggregate_hourly_prices() — first run")

    aggregate_hourly_prices()

    rows1 = db.query(PriceByHour).filter(PriceByHour.p_id == juice.p_id).all()
    print(f"  [RESULT] After 1st run: avg=${rows1[0].price:.2f}")

    # Add another submission and run again
    sub2 = add_submission(db, user, [(juice, 7.00)], created_at=now - timedelta(minutes=5))
    print(f"  [INSERT] Submission 2: juice=$7.00, created_at={sub2.created_at}")
    print(f"  [RUN]    aggregate_hourly_prices() — second run")

    aggregate_hourly_prices()

    rows = db.query(PriceByHour).filter(PriceByHour.p_id == juice.p_id).all()
    print(f"  [RESULT] After 2nd run: rows={len(rows)}, avg=${rows[0].price:.2f} (expected $3.00 — original preserved)")

    assert len(rows) == 1
    assert rows[0].price == 3.00  # original value preserved
