import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal
# Explicitly import models to register them with Base.metadata
from app import models
from app.routes import catalog
from app.seed import seed_catalog_data

# Create tables and Seed
print("Initializing Database...")
try:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_catalog_data(db)
    db.close()
    print("Database initialization complete.")
except Exception as e:
    print(f"CRITICAL ERROR during DB init: {e}")
    sys.exit(1)

app = FastAPI(
    title="Catalog Service",
    description="Microservice for product management",
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
    return {"status": "ok", "service": "catalog"}

app.include_router(catalog.router)
