import random
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.grocery_item import GroceryItem
from app.models.price_submission import PriceSubmission
from app.models.store import Store
from app.models.user import User
from app.services.unit_conversion import parse_unit_string

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
        {"name": "2% Milk", "brand": "Natrel", "unit": "2L", "base_price": 5.49},
        {"name": "Skim Milk", "brand": "Natrel", "unit": "2L", "base_price": 5.29},
        {"name": "Butter", "brand": "Lactantia", "unit": "454g", "base_price": 5.99},
        {"name": "Cheddar Cheese", "brand": "Black Diamond", "unit": "400g", "base_price": 8.49},
        {"name": "Mozzarella Cheese", "brand": "Saputo", "unit": "340g", "base_price": 6.99},
        {"name": "Parmesan Cheese", "brand": "Saputo", "unit": "250g", "base_price": 8.99},
        {"name": "Greek Yogurt", "brand": "Liberté", "unit": "750g", "base_price": 6.29},
        {"name": "Yogurt", "brand": "Danone", "unit": "650g", "base_price": 4.49},
        {"name": "Cream Cheese", "brand": "Philadelphia", "unit": "250g", "base_price": 4.49},
        {"name": "Sour Cream", "brand": "Natrel", "unit": "500ml", "base_price": 3.49},
        {"name": "Heavy Cream", "brand": "Natrel", "unit": "473ml", "base_price": 4.29},
        {"name": "Eggs", "brand": None, "unit": "12 pack", "base_price": 4.49},
        {"name": "Margarine", "brand": "Becel", "unit": "454g", "base_price": 4.99},
        {"name": "Shredded Cheese", "brand": "Black Diamond", "unit": "340g", "base_price": 6.49},
    ],
    "Produce": [
        {"name": "Bananas", "brand": None, "unit": "per lb", "base_price": 0.79},
        {"name": "Avocados", "brand": None, "unit": "each", "base_price": 2.49},
        {"name": "Baby Spinach", "brand": "Dole", "unit": "312g", "base_price": 4.99},
        {"name": "Red Bell Peppers", "brand": None, "unit": "each", "base_price": 1.99},
        {"name": "Green Bell Peppers", "brand": None, "unit": "each", "base_price": 1.49},
        {"name": "Russet Potatoes", "brand": None, "unit": "10lb bag", "base_price": 5.99},
        {"name": "Tomatoes", "brand": None, "unit": "per lb", "base_price": 2.49},
        {"name": "Roma Tomatoes", "brand": None, "unit": "per lb", "base_price": 2.29},
        {"name": "Cherry Tomatoes", "brand": None, "unit": "454g", "base_price": 4.99},
        {"name": "Onions", "brand": None, "unit": "3lb bag", "base_price": 3.49},
        {"name": "Red Onions", "brand": None, "unit": "per lb", "base_price": 1.99},
        {"name": "Garlic", "brand": None, "unit": "each", "base_price": 0.99},
        {"name": "Carrots", "brand": None, "unit": "2lb bag", "base_price": 2.49},
        {"name": "Celery", "brand": None, "unit": "each", "base_price": 2.99},
        {"name": "Broccoli", "brand": None, "unit": "each", "base_price": 2.99},
        {"name": "Cauliflower", "brand": None, "unit": "each", "base_price": 3.99},
        {"name": "Cucumber", "brand": None, "unit": "each", "base_price": 1.49},
        {"name": "Lettuce", "brand": None, "unit": "each", "base_price": 2.49},
        {"name": "Romaine Lettuce", "brand": None, "unit": "each", "base_price": 2.99},
        {"name": "Mushrooms", "brand": None, "unit": "227g", "base_price": 3.49},
        {"name": "Apples", "brand": None, "unit": "per lb", "base_price": 1.99},
        {"name": "Oranges", "brand": None, "unit": "per lb", "base_price": 1.49},
        {"name": "Lemons", "brand": None, "unit": "each", "base_price": 0.79},
        {"name": "Limes", "brand": None, "unit": "each", "base_price": 0.59},
        {"name": "Strawberries", "brand": None, "unit": "454g", "base_price": 4.99},
        {"name": "Blueberries", "brand": None, "unit": "312g", "base_price": 4.49},
        {"name": "Grapes", "brand": None, "unit": "per lb", "base_price": 3.49},
        {"name": "Watermelon", "brand": None, "unit": "each", "base_price": 7.99},
        {"name": "Sweet Potatoes", "brand": None, "unit": "per lb", "base_price": 1.99},
        {"name": "Zucchini", "brand": None, "unit": "each", "base_price": 1.49},
        {"name": "Green Beans", "brand": None, "unit": "per lb", "base_price": 3.49},
        {"name": "Corn", "brand": None, "unit": "each", "base_price": 1.29},
        {"name": "Ginger", "brand": None, "unit": "per lb", "base_price": 5.99},
        {"name": "Jalapeño Peppers", "brand": None, "unit": "per lb", "base_price": 3.99},
        {"name": "Kale", "brand": None, "unit": "each", "base_price": 2.99},
        {"name": "Green Onions", "brand": None, "unit": "each", "base_price": 1.29},
        {"name": "Cilantro", "brand": None, "unit": "each", "base_price": 1.29},
        {"name": "Parsley", "brand": None, "unit": "each", "base_price": 1.29},
    ],
    "Meat": [
        {"name": "Chicken Breast", "brand": "Maple Leaf", "unit": "per kg", "base_price": 13.99},
        {"name": "Chicken Thighs", "brand": "Maple Leaf", "unit": "per kg", "base_price": 10.99},
        {"name": "Chicken Drumsticks", "brand": None, "unit": "per kg", "base_price": 7.99},
        {"name": "Chicken Wings", "brand": None, "unit": "per kg", "base_price": 11.99},
        {"name": "Whole Chicken", "brand": None, "unit": "per kg", "base_price": 8.99},
        {"name": "Ground Beef", "brand": None, "unit": "per kg", "base_price": 11.49},
        {"name": "Lean Ground Beef", "brand": None, "unit": "per kg", "base_price": 13.99},
        {"name": "Beef Steak", "brand": None, "unit": "per kg", "base_price": 24.99},
        {"name": "Stewing Beef", "brand": None, "unit": "per kg", "base_price": 15.99},
        {"name": "Pork Chops", "brand": None, "unit": "per kg", "base_price": 9.99},
        {"name": "Pork Tenderloin", "brand": None, "unit": "per kg", "base_price": 14.99},
        {"name": "Ground Pork", "brand": None, "unit": "per kg", "base_price": 9.49},
        {"name": "Bacon", "brand": "Maple Leaf", "unit": "375g", "base_price": 7.49},
        {"name": "Ham", "brand": None, "unit": "per kg", "base_price": 8.99},
        {"name": "Turkey Breast", "brand": None, "unit": "per kg", "base_price": 15.99},
        {"name": "Ground Turkey", "brand": None, "unit": "per kg", "base_price": 12.99},
        {"name": "Sausages", "brand": "Maple Leaf", "unit": "450g", "base_price": 6.99},
        {"name": "Hot Dogs", "brand": "Maple Leaf", "unit": "375g", "base_price": 4.99},
        {"name": "Salmon Fillet", "brand": None, "unit": "per kg", "base_price": 22.99},
        {"name": "Shrimp", "brand": None, "unit": "454g", "base_price": 12.99},
        {"name": "Tilapia Fillet", "brand": None, "unit": "per kg", "base_price": 15.99},
        {"name": "Cod Fillet", "brand": None, "unit": "per kg", "base_price": 17.99},
        {"name": "Deli Turkey", "brand": None, "unit": "200g", "base_price": 5.99},
        {"name": "Deli Ham", "brand": None, "unit": "200g", "base_price": 5.49},
    ],
    "Bakery": [
        {"name": "White Bread", "brand": "Dempster's", "unit": "675g", "base_price": 3.99},
        {"name": "Whole Wheat Bread", "brand": "Dempster's", "unit": "675g", "base_price": 4.29},
        {"name": "Multigrain Bread", "brand": "Dempster's", "unit": "675g", "base_price": 4.49},
        {"name": "Bagels", "brand": "Dempster's", "unit": "6 pack", "base_price": 4.49},
        {"name": "English Muffins", "brand": "Dempster's", "unit": "6 pack", "base_price": 3.99},
        {"name": "Croissants", "brand": None, "unit": "4 pack", "base_price": 5.99},
        {"name": "Tortillas", "brand": "Old El Paso", "unit": "10 pack", "base_price": 4.29},
        {"name": "Pita Bread", "brand": None, "unit": "6 pack", "base_price": 3.49},
        {"name": "Naan Bread", "brand": None, "unit": "4 pack", "base_price": 4.49},
        {"name": "Hamburger Buns", "brand": "Dempster's", "unit": "8 pack", "base_price": 3.99},
        {"name": "Hot Dog Buns", "brand": "Dempster's", "unit": "8 pack", "base_price": 3.99},
        {"name": "Dinner Rolls", "brand": None, "unit": "12 pack", "base_price": 4.99},
        {"name": "Muffins", "brand": None, "unit": "6 pack", "base_price": 5.99},
    ],
    "Beverages": [
        {"name": "Orange Juice", "brand": "Tropicana", "unit": "1.75L", "base_price": 5.99},
        {"name": "Apple Juice", "brand": "Oasis", "unit": "1.75L", "base_price": 3.99},
        {"name": "Coffee", "brand": "Tim Hortons", "unit": "300g", "base_price": 9.99},
        {"name": "Tea", "brand": "Red Rose", "unit": "72 pack", "base_price": 5.49},
        {"name": "Sparkling Water", "brand": "Montellier", "unit": "12 pack", "base_price": 5.49},
        {"name": "Water Bottles", "brand": "Nestlé", "unit": "24 pack", "base_price": 3.99},
        {"name": "Cola", "brand": "Coca-Cola", "unit": "2L", "base_price": 2.49},
        {"name": "Ginger Ale", "brand": "Canada Dry", "unit": "2L", "base_price": 2.49},
        {"name": "Lemonade", "brand": None, "unit": "1.75L", "base_price": 3.49},
        {"name": "Almond Milk", "brand": "Silk", "unit": "1.89L", "base_price": 4.99},
        {"name": "Oat Milk", "brand": "Oatly", "unit": "1.89L", "base_price": 5.49},
        {"name": "Cranberry Juice", "brand": "Ocean Spray", "unit": "1.89L", "base_price": 4.49},
    ],
    "Pantry": [
        {"name": "Pasta", "brand": "Barilla", "unit": "454g", "base_price": 2.49},
        {"name": "Spaghetti", "brand": "Barilla", "unit": "454g", "base_price": 2.49},
        {"name": "Penne", "brand": "Barilla", "unit": "454g", "base_price": 2.49},
        {"name": "Rice", "brand": None, "unit": "2kg", "base_price": 5.99},
        {"name": "Basmati Rice", "brand": None, "unit": "2kg", "base_price": 7.99},
        {"name": "Peanut Butter", "brand": "Kraft", "unit": "1kg", "base_price": 6.99},
        {"name": "Maple Syrup", "brand": "Selection", "unit": "540ml", "base_price": 8.99},
        {"name": "Canned Tomatoes", "brand": "Unico", "unit": "796ml", "base_price": 2.29},
        {"name": "Tomato Sauce", "brand": "Unico", "unit": "680ml", "base_price": 2.49},
        {"name": "Tomato Paste", "brand": "Unico", "unit": "156ml", "base_price": 1.29},
        {"name": "Pasta Sauce", "brand": "Ragú", "unit": "640ml", "base_price": 3.99},
        {"name": "Olive Oil", "brand": "Bertolli", "unit": "1L", "base_price": 9.99},
        {"name": "Vegetable Oil", "brand": None, "unit": "1L", "base_price": 4.49},
        {"name": "Canola Oil", "brand": None, "unit": "1L", "base_price": 4.99},
        {"name": "Flour", "brand": "Five Roses", "unit": "2.5kg", "base_price": 5.49},
        {"name": "Sugar", "brand": "Redpath", "unit": "2kg", "base_price": 4.49},
        {"name": "Brown Sugar", "brand": "Redpath", "unit": "1kg", "base_price": 3.99},
        {"name": "Salt", "brand": "Windsor", "unit": "1kg", "base_price": 2.49},
        {"name": "Black Pepper", "brand": "Club House", "unit": "100g", "base_price": 5.99},
        {"name": "Ketchup", "brand": "Heinz", "unit": "750ml", "base_price": 4.99},
        {"name": "Mustard", "brand": "French's", "unit": "400ml", "base_price": 3.49},
        {"name": "Mayonnaise", "brand": "Hellmann's", "unit": "710ml", "base_price": 5.99},
        {"name": "Soy Sauce", "brand": "Kikkoman", "unit": "591ml", "base_price": 4.49},
        {"name": "Vinegar", "brand": "Heinz", "unit": "500ml", "base_price": 2.99},
        {"name": "Canned Corn", "brand": "Green Giant", "unit": "341ml", "base_price": 1.79},
        {"name": "Canned Beans", "brand": "Unico", "unit": "540ml", "base_price": 1.49},
        {"name": "Canned Chickpeas", "brand": "Unico", "unit": "540ml", "base_price": 1.49},
        {"name": "Canned Tuna", "brand": "Clover Leaf", "unit": "170g", "base_price": 2.49},
        {"name": "Cereal", "brand": "Cheerios", "unit": "430g", "base_price": 5.99},
        {"name": "Oatmeal", "brand": "Quaker", "unit": "1kg", "base_price": 5.49},
        {"name": "Granola Bars", "brand": "Nature Valley", "unit": "6 pack", "base_price": 4.49},
        {"name": "Crackers", "brand": "Christie", "unit": "450g", "base_price": 4.99},
        {"name": "Chips", "brand": "Lay's", "unit": "235g", "base_price": 4.49},
        {"name": "Salsa", "brand": "Tostitos", "unit": "416ml", "base_price": 4.49},
        {"name": "Honey", "brand": "Billy Bee", "unit": "500g", "base_price": 7.99},
        {"name": "Jam", "brand": "Smucker's", "unit": "500ml", "base_price": 4.99},
        {"name": "Chicken Broth", "brand": "Campbell's", "unit": "900ml", "base_price": 2.99},
        {"name": "Coconut Milk", "brand": None, "unit": "400ml", "base_price": 2.49},
    ],
}

STORES = [
    {"name": "Loblaws", "address": "60 Carlton St, Toronto, ON", "lat": 43.6612, "lng": -79.3797, "city": "Toronto", "province": "ON", "postal_code": "M5B 1J2"},
    {"name": "Metro", "address": "10 Lower Jarvis St, Toronto, ON", "lat": 43.6488, "lng": -79.3716, "city": "Toronto", "province": "ON", "postal_code": "M5E 1Z2"},
    {"name": "No Frills", "address": "280 Spadina Ave, Toronto, ON", "lat": 43.6532, "lng": -79.3970, "city": "Toronto", "province": "ON", "postal_code": "M5T 3A5"},
    {"name": "Walmart", "address": "900 Dufferin St, Toronto, ON", "lat": 43.6571, "lng": -79.4350, "city": "Toronto", "province": "ON", "postal_code": "M6H 4A9"},
    {"name": "Costco", "address": "100 Billy Bishop Way, Toronto, ON", "lat": 43.7315, "lng": -79.2870, "city": "Toronto", "province": "ON", "postal_code": "M3K 2C8"},
]
STORE_NAMES = [s["name"] for s in STORES]


def run_seed(db: Session) -> dict:
    if db.query(Category).count() > 0:
        return {"message": "Database already seeded", "seeded": False}

    random.seed(42)
    today = date.today()
    category_map: dict[str, Category] = {}

    # Create default user
    default_user = User(email="dev@hackcanada.com", username="dev")
    db.add(default_user)
    db.flush()

    # Create stores with coordinates
    store_map: dict[str, Store] = {}
    for store_data in STORES:
        store = Store(**store_data)
        db.add(store)
        db.flush()
        store_map[store.name] = store

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

            # Parse weight from unit string
            weight_value, weight_unit = parse_unit_string(item_data["unit"])

            item = GroceryItem(
                category_id=cat.id,
                weight_value=weight_value,
                weight_unit=weight_unit,
                is_new=False,
                confirmation_count=10,
                **item_data,
            )
            db.add(item)
            db.flush()
            total_items += 1

            price = base_price
            for day_offset in range(365, 0, -1):
                obs_date = today - timedelta(days=day_offset)
                change = random.gauss(0, 0.02)
                price = max(0.50, price * (1 + change))
                store = store_map[random.choice(STORE_NAMES)]
                sub = PriceSubmission(
                    item_id=item.id,
                    price=round(price, 2),
                    store_id=store.id,
                    date_observed=obs_date,
                )
                db.add(sub)
                total_submissions += 1

    db.commit()
    return {
        "message": "Seed complete",
        "seeded": True,
        "categories": len(CATEGORIES),
        "items": total_items,
        "submissions": total_submissions,
        "stores": len(STORE_NAMES),
    }
