import random
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.grocery_item import GroceryItem
from app.models.price_submission import PriceSubmission

CATEGORIES = [
    {"name": "Dairy", "icon": "milk"},
    {"name": "Produce", "icon": "carrot"},
    {"name": "Meat", "icon": "drumstick"},
    {"name": "Bakery", "icon": "bread"},
    {"name": "Beverages", "icon": "coffee"},
    {"name": "Pantry", "icon": "jar"},
]

ITEMS = {
    "Dairy": [
        {"name": "Whole Milk", "brand": "Natrel", "unit": "2L", "base_price": 5.49},
        {"name": "Butter", "brand": "Lactantia", "unit": "454g", "base_price": 5.99},
        {"name": "Cheddar Cheese", "brand": "Black Diamond", "unit": "400g", "base_price": 8.49},
        {"name": "Greek Yogurt", "brand": "Liberté", "unit": "750g", "base_price": 6.29},
        {"name": "Cream Cheese", "brand": "Philadelphia", "unit": "250g", "base_price": 4.49},
    ],
    "Produce": [
        {"name": "Bananas", "brand": None, "unit": "per lb", "base_price": 0.79},
        {"name": "Avocados", "brand": None, "unit": "each", "base_price": 2.49},
        {"name": "Baby Spinach", "brand": "Dole", "unit": "312g", "base_price": 4.99},
        {"name": "Red Bell Peppers", "brand": None, "unit": "each", "base_price": 1.99},
        {"name": "Russet Potatoes", "brand": None, "unit": "10lb bag", "base_price": 5.99},
    ],
    "Meat": [
        {"name": "Chicken Breast", "brand": "Maple Leaf", "unit": "per kg", "base_price": 13.99},
        {"name": "Ground Beef", "brand": "Medium", "unit": "per kg", "base_price": 11.49},
        {"name": "Pork Chops", "brand": None, "unit": "per kg", "base_price": 9.99},
        {"name": "Bacon", "brand": "Maple Leaf", "unit": "375g", "base_price": 7.49},
    ],
    "Bakery": [
        {"name": "White Bread", "brand": "Dempster's", "unit": "675g", "base_price": 3.99},
        {"name": "Bagels", "brand": "Dempster's", "unit": "6 pack", "base_price": 4.49},
        {"name": "Croissants", "brand": None, "unit": "4 pack", "base_price": 5.99},
        {"name": "Tortillas", "brand": "Old El Paso", "unit": "10 pack", "base_price": 4.29},
    ],
    "Beverages": [
        {"name": "Orange Juice", "brand": "Tropicana", "unit": "1.75L", "base_price": 5.99},
        {"name": "Coffee", "brand": "Tim Hortons", "unit": "300g", "base_price": 9.99},
        {"name": "Sparkling Water", "brand": "Montellier", "unit": "12 pack", "base_price": 5.49},
    ],
    "Pantry": [
        {"name": "Pasta", "brand": "Barilla", "unit": "454g", "base_price": 2.49},
        {"name": "Peanut Butter", "brand": "Kraft", "unit": "1kg", "base_price": 6.99},
        {"name": "Maple Syrup", "brand": "Selection", "unit": "540ml", "base_price": 8.99},
        {"name": "Canned Tomatoes", "brand": "Unico", "unit": "796ml", "base_price": 2.29},
    ],
}

STORES = ["Loblaws", "Metro", "No Frills", "Walmart", "Costco"]


def run_seed(db: Session) -> dict:
    if db.query(Category).count() > 0:
        return {"message": "Database already seeded", "seeded": False}

    random.seed(42)
    today = date.today()
    category_map: dict[str, Category] = {}

    for cat_data in CATEGORIES:
        cat = Category(**cat_data)
        db.add(cat)
        db.flush()
        category_map[cat.name] = cat

    total_items = 0
    total_submissions = 0

    for cat_name, item_list in ITEMS.items():
        cat = category_map[cat_name]
        for item_data in item_list:
            base_price = item_data.pop("base_price")
            item = GroceryItem(category_id=cat.id, **item_data)
            db.add(item)
            db.flush()
            total_items += 1

            price = base_price
            for day_offset in range(30, 0, -1):
                obs_date = today - timedelta(days=day_offset)
                change = random.gauss(0, 0.05)
                price = max(0.50, price * (1 + change))
                store = random.choice(STORES)
                sub = PriceSubmission(
                    item_id=item.id,
                    price=round(price, 2),
                    store_name=store,
                    date_observed=obs_date,
                )
                db.add(sub)
                total_submissions += 1

            item.current_price = round(price, 2)
            if base_price > 0:
                item.price_change_pct = round(
                    ((price - base_price) / base_price) * 100, 2
                )

    db.commit()
    return {
        "message": "Seed complete",
        "seeded": True,
        "categories": len(CATEGORIES),
        "items": total_items,
        "submissions": total_submissions,
    }
