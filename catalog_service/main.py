import time
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, create_engine
from app.database import engine, Base, SessionLocal, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from app import models
from app.routes import catalog
from app.seed import seed_catalog_data


def ensure_database_exists():
    postgres_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
    temp_engine = create_engine(postgres_url, isolation_level="AUTOCOMMIT")

    with temp_engine.connect() as conn:
        result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'"))
        if not result.scalar():
            print(f"Database {DB_NAME} does not exist. Creating...")
            conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
            print(f"Database {DB_NAME} created.")
        else:
            print(f"Database {DB_NAME} already exists.")
    temp_engine.dispose()


print("Initializing Database...")
max_retries = 15
retry_delay = 5
for attempt in range(max_retries):
    try:
        ensure_database_exists()
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        seed_catalog_data(db)
        db.close()
        print("Database initialization complete.")
        break
    except Exception as e:
        print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
        else:
            print("CRITICAL ERROR: Database initialization failed after max retries.")
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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
