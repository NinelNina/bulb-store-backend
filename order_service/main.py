from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal
from app import models
from app.routes import orders

def seed_reference_data(db: SessionLocal):
    states = [
        (1, 'IN_PROCESS', 'Order is being processed'),
        (2, 'IN_TRANSIT', 'Order is on its way'),
        (3, 'DELIVERED', 'Order has been delivered to site'),
        (4, 'RECEIVED', 'Order has been received by customer'),
        (5, 'REJECTED', 'Order has been rejected')
    ]
    for id, name, desc in states:
        if not db.query(models.OrderState).filter(models.OrderState.id == id).first():
            db.add(models.OrderState(id=id, name=name, description=desc))
    
    payments = [
        (1, 'PENDING', 'Payment is pending'),
        (2, 'PAID', 'Order is paid'),
        (3, 'REFUNDED', 'Payment has been refunded'),
        (4, 'CANCELLED', 'Payment was cancelled')
    ]
    for id, name, desc in payments:
        if not db.query(models.PaymentState).filter(models.PaymentState.id == id).first():
            db.add(models.PaymentState(id=id, name=name, description=desc))
            
    deliveries = [
        (1, 'CDEK', 'CDEK delivery service'),
        (2, 'YANDEX', 'Yandex delivery service'),
        (3, 'POST', 'Russian Post'),
        (4, 'BOXBERRY', 'Boxberry delivery service'),
        (5, 'САМОВЫВОЗ', 'Local pickup')
    ]
    for id, name, desc in deliveries:
        if not db.query(models.DeliveryType).filter(models.DeliveryType.id == id).first():
            db.add(models.DeliveryType(id=id, name=name, description=desc))
    
    db.commit()

try:
    Base.metadata.create_all(bind=engine)
    db_session = SessionLocal()
    seed_reference_data(db_session)
    db_session.close()
except Exception as e:
    print(f"Error creating/seeding tables: {e}")

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

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8081)
