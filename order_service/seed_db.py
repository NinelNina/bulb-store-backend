import uuid
from sqlalchemy import create_engine, Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "bulbstore")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class OrderState(Base):
    __tablename__ = "order_states"
    id = Column(SmallInteger, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255))


class PaymentState(Base):
    __tablename__ = "payment_states"
    id = Column(SmallInteger, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255))


class DeliveryType(Base):
    __tablename__ = "delivery_types"
    id = Column(SmallInteger, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255))


def seed():
    print("Ensuring tables are created...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        states = [
            (1, 'IN_PROCESS', 'Order is being processed'),
            (2, 'IN_TRANSIT', 'Order is on its way'),
            (3, 'DELIVERED', 'Order has been delivered to site'),
            (4, 'RECEIVED', 'Order has been received by customer'),
            (5, 'REJECTED', 'Order has been rejected')
        ]
        for id, name, desc in states:
            if not db.query(OrderState).filter(OrderState.id == id).first():
                db.add(OrderState(id=id, name=name, description=desc))

        payments = [
            (1, 'PENDING', 'Payment is pending'),
            (2, 'PAID', 'Order is paid'),
            (3, 'REFUNDED', 'Payment has been refunded'),
            (4, 'CANCELLED', 'Payment was cancelled')
        ]
        for id, name, desc in payments:
            if not db.query(PaymentState).filter(PaymentState.id == id).first():
                db.add(PaymentState(id=id, name=name, description=desc))

        deliveries = [
            (1, 'CDEK', 'CDEK delivery service'),
            (2, 'YANDEX', 'Yandex delivery service'),
            (3, 'POST', 'Russian Post'),
            (4, 'BOXBERRY', 'Boxberry delivery service'),
            (5, 'САМОВЫВОЗ', 'Local pickup')
        ]
        for id, name, desc in deliveries:
            if not db.query(DeliveryType).filter(DeliveryType.id == id).first():
                db.add(DeliveryType(id=id, name=name, description=desc))

        db.commit()
        print("Order Service reference data seeded!")
    except Exception as e:
        print(f"Error seeding Order Service: {e}")
        db.rollback()
        raise SystemExit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
