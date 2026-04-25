import uuid
from sqlalchemy import create_engine, Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
import os

# Database Connection
# Use db:5432 if running inside Docker, localhost:5436 if running from host
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "bulbstore")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Models (Re-defined for seeding to avoid import issues)
class Category(Base):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False)


class Product(Base):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    socket = Column(String, nullable=False)
    power = Column(Integer, nullable=False)
    color_temperature = Column(Integer, nullable=False)
    brightness = Column(Integer, nullable=False)
    shape = Column(String)
    description = Column(String)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, default=0)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    is_deleted = Column(Boolean, default=False)


def seed():
    # Create tables before seeding
    print("Ensuring tables are created...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Create Categories
        categories_data = [
            {"name": "Светодиодные лампы (LED)"},
            {"name": "Умные лампы (Smart)"},
            {"name": "Винтажные ламп (Filament)"},
            {"name": "Декоративные лампы"}
        ]

        db_categories = {}
        for cat in categories_data:
            existing = db.query(Category).filter(Category.name == cat["name"]).first()
            if not existing:
                new_cat = Category(id=uuid.uuid4(), name=cat["name"])
                db.add(new_cat)
                db_categories[cat["name"]] = new_cat
            else:
                db_categories[cat["name"]] = existing

        db.commit()
        print("Categories seeded.")

        # 2. Create Products
        products_data = [
            {
                "name": "Philips LED Classic E27",
                "socket": "E27",
                "power": 8,
                "color_temperature": 2700,
                "brightness": 806,
                "shape": "A60",
                "description": "Классическая теплая лампа для дома",
                "price": 450.00,
                "quantity": 100,
                "category": "Светодиодные лампы (LED)"
            },
            {
                "name": "Xiaomi Mi Smart Bulb Essential",
                "socket": "E27",
                "power": 9,
                "color_temperature": 6500,
                "brightness": 950,
                "shape": "A60",
                "description": "Умная лампа RGB с управлением через Wi-Fi",
                "price": 1290.00,
                "quantity": 45,
                "category": "Умные лампы (Smart)"
            },
            {
                "name": "Gauss Filament Amber",
                "socket": "E14",
                "power": 5,
                "color_temperature": 2400,
                "brightness": 420,
                "shape": "C35",
                "description": "Золотистая ретро-лампа 'свеча на ветру'",
                "price": 320.00,
                "quantity": 30,
                "category": "Винтажные ламп (Filament)"
            },
            {
                "name": "Yeelight Smart LED Bulb W3",
                "socket": "E27",
                "power": 8,
                "color_temperature": 4000,
                "brightness": 900,
                "shape": "A60",
                "description": "Экономичная умная лампа",
                "price": 890.00,
                "quantity": 60,
                "category": "Умные лампы (Smart)"
            },
            {
                "name": "Osram Retrofit LED",
                "socket": "GU10",
                "power": 4,
                "color_temperature": 3000,
                "brightness": 350,
                "shape": "Reflector",
                "description": "Точечный светильник для встраиваемых потолков",
                "price": 190.00,
                "quantity": 200,
                "category": "Светодиодные лампы (LED)"
            }
        ]

        for prod in products_data:
            existing = db.query(Product).filter(Product.name == prod["name"]).first()
            if not existing:
                cat_name = prod.pop("category")
                new_prod = Product(
                    id=uuid.uuid4(),
                    **prod,
                    category_id=db_categories[cat_name].id
                )
                db.add(new_prod)

        db.commit()
        print("Products seeded.")
        print("Seeding completed successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise SystemExit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
