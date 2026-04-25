import uuid
from sqlalchemy.orm import Session
from app import models


def seed_catalog_data(db: Session):
    # 1. Categories
    categories_data = [
        {"name": "Светодиодные лампы (LED)"},
        {"name": "Умные лампы (Smart)"},
        {"name": "Винтажные ламп (Filament)"},
        {"name": "Декоративные лампы"}
    ]

    db_categories = {}
    for cat in categories_data:
        existing = db.query(models.Category).filter(models.Category.name == cat["name"]).first()
        if not existing:
            new_cat = models.Category(id=uuid.uuid4(), name=cat["name"])
            db.add(new_cat)
            db_categories[cat["name"]] = new_cat
            print(f"Created category: {cat['name']}")
        else:
            db_categories[cat["name"]] = existing

    db.commit()

    # 2. Products
    products_data = [
        {
            "name": "Philips LED Classic E27",
            "socket": "E27", "power": 8, "color_temperature": 2700, "brightness": 806,
            "shape": "A60", "description": "Классическая теплая лампа", "price": 450.00,
            "quantity": 100, "category": "Светодиодные лампы (LED)"
        },
        {
            "name": "Xiaomi Mi Smart Bulb Essential",
            "socket": "E27", "power": 9, "color_temperature": 6500, "brightness": 950,
            "shape": "A60", "description": "RGB с Wi-Fi", "price": 1290.00,
            "quantity": 45, "category": "Умные лампы (Smart)"
        }
    ]

    for prod in products_data:
        existing = db.query(models.Product).filter(models.Product.name == prod["name"]).first()
        if not existing:
            cat_name = prod.pop("category")
            new_prod = models.Product(
                id=uuid.uuid4(),
                **prod,
                category_id=db_categories[cat_name].id
            )
            db.add(new_prod)
            print(f"Created product: {prod['name']}")

    db.commit()
