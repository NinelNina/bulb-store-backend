import sys
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
from sqlalchemy import text
from app.database import engine, Base, SessionLocal
from app import models
from app.routes import orders
from app.seed import seed_order_data

# Create tables and Seed
print("Initializing Database...")
try:
    # Wait for catalog-service to create the specific shared table
    print("Waiting for Catalog Service to initialize 'products' table...")
    retries = 10
    product_table_exists = False

    with engine.connect() as conn:
        for _ in range(retries):
            # Check if products table exists in postgres
            result = conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'products');"))
            if result.scalar():
                product_table_exists = True
                break
            time.sleep(2)
            print("Still waiting for 'products' table...")

    if not product_table_exists:
        print(
            "WARNING: 'products' table not found after waiting. Proceeding anyway, but ForeignKey creation might fail.")

    # Do not attempt to create the 'products' table from Order Service,
    # as Catalog Service owns it and should create the full schema.
    tables_to_create = [
        table for table in Base.metadata.sorted_tables
        if table.name != "products"
    ]
    Base.metadata.create_all(bind=engine, tables=tables_to_create)

    db = SessionLocal()
    seed_order_data(db)
    db.close()
    print("Database initialization complete.")
except Exception as e:
    print(f"Error during DB init: {e}")
    sys.exit(1)

app = FastAPI(
    title="Order Service",
    description="Microservice for order management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "orders"}


app.include_router(orders.router)