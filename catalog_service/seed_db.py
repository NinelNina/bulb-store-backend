from app.database import engine, Base, SessionLocal
from app.seed import seed_catalog_data


def seed():
    print("Ensuring tables are created...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_catalog_data(db)
        print("Seeding completed successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise SystemExit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
