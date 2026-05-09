import sys
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
from sqlalchemy import text
from app.database import engine, Base, SessionLocal
from app import models
from app.routes import orders
from app.seed import seed_order_data

print("Initializing Database...")
max_retries = 10
retry_delay = 5
for attempt in range(max_retries):
    try:
        Base.metadata.create_all(bind=engine)

        db = SessionLocal()
        seed_order_data(db)
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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081)
