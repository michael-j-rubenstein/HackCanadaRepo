"""
Database seeder script.
Loads CSV data and generates hourly price data.

Usage:
    docker-compose exec backend python -m migrations.seed
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from app.database import engine, Base
from app.models import (
    Category, Brand, Store, ProductItem, User, PriceByHour,
    CartItem, Submission, SubmissionItem
)


SEED_DATA_DIR = Path(__file__).parent / "seed_data"

# Date range: March 3, 2026 00:00 to March 8, 2026 10:00
START_DATE = datetime(2026, 3, 3, 0, 0)
END_DATE = datetime(2026, 3, 8, 10, 0)


def load_csv(filename: str) -> list[dict]:
    """Load a CSV file and return list of dicts."""
    filepath = SEED_DATA_DIR / filename
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)


def seed_stores(session: Session) -> None:
    """Seed stores table."""
    rows = load_csv("stores.csv")
    for row in rows:
        store = Store(store_id=row["store_id"], name=row["name"])
        session.add(store)
    session.commit()
    print(f"Seeded {len(rows)} stores")


def seed_brands(session: Session) -> None:
    """Seed brands table."""
    rows = load_csv("brands.csv")
    for row in rows:
        brand = Brand(brand_id=row["brand_id"], name=row["name"])
        session.add(brand)
    session.commit()
    print(f"Seeded {len(rows)} brands")


def seed_categories(session: Session) -> None:
    """Seed categories table."""
    rows = load_csv("categories.csv")
    for row in rows:
        category = Category(c_id=row["c_id"], name=row["name"], unit=row["unit"])
        session.add(category)
    session.commit()
    print(f"Seeded {len(rows)} categories")


def seed_users(session: Session) -> None:
    """Seed users table."""
    rows = load_csv("users.csv")
    for row in rows:
        user = User(u_id=row["u_id"], name=row["name"])
        session.add(user)
    session.commit()
    print(f"Seeded {len(rows)} users")


def seed_products(session: Session) -> dict[str, float]:
    """Seed products table. Returns dict of p_id -> base_price."""
    rows = load_csv("products.csv")
    base_prices = {}
    for row in rows:
        product = ProductItem(
            p_id=row["p_id"],
            name=row["name"],
            c_id=row["c_id"],
            brand_id=row["brand_id"],
            store_id=row["store_id"],
        )
        session.add(product)
        base_prices[row["p_id"]] = float(row["base_price"])
    session.commit()
    print(f"Seeded {len(rows)} products")
    return base_prices


def seed_price_by_hour(session: Session, base_prices: dict[str, float]) -> None:
    """Generate hourly price data with small random variations."""
    current = START_DATE
    count = 0

    while current <= END_DATE:
        for p_id, base_price in base_prices.items():
            # Add random variation of +/- 5%
            variation = random.uniform(-0.05, 0.05)
            price = round(base_price * (1 + variation), 2)

            price_record = PriceByHour(
                p_id=p_id,
                timestamp=current,
                price=price,
            )
            session.add(price_record)
            count += 1

        current += timedelta(hours=1)

    session.commit()
    print(f"Seeded {count} price_by_hour records")


def clear_tables(session: Session) -> None:
    """Clear all tables in reverse FK order."""
    session.execute(SubmissionItem.__table__.delete())
    session.execute(Submission.__table__.delete())
    session.execute(CartItem.__table__.delete())
    session.execute(PriceByHour.__table__.delete())
    session.execute(ProductItem.__table__.delete())
    session.execute(User.__table__.delete())
    session.execute(Category.__table__.delete())
    session.execute(Brand.__table__.delete())
    session.execute(Store.__table__.delete())
    session.commit()
    print("Cleared existing data")


def run_seed():
    """Run all seeders."""
    print("Starting database seed...")

    with Session(engine) as session:
        # Clear existing data first
        clear_tables(session)
        # Seed in order (respecting FK constraints)
        seed_stores(session)
        seed_brands(session)
        seed_categories(session)
        seed_users(session)
        base_prices = seed_products(session)
        seed_price_by_hour(session, base_prices)

    print("Database seeding complete!")


if __name__ == "__main__":
    run_seed()
