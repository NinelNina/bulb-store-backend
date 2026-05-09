from app.database import engine, Base, SessionLocal
from app.seed import seed_order_data

def seed():
    print("Ensuring tables are created...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_order_data(db)
        print("Order Service reference data seeded!")
    except Exception as e:
        print(f"Error seeding Order Service: {e}")
        db.rollback()
        raise SystemExit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed()
