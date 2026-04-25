import uuid
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String)
    quantity = Column(Integer)
    price = Column(Numeric(10, 2))

class OrderState(Base):
    __tablename__ = "order_state"
    id = Column(SmallInteger, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PaymentState(Base):
    __tablename__ = "payment_state"
    id = Column(SmallInteger, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DeliveryType(Base):
    __tablename__ = "delivery_types"
    id = Column(SmallInteger, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Order(Base):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String, unique=True, nullable=False)
    order_state_id = Column(SmallInteger, ForeignKey("order_state.id"))
    phone_number = Column(String, nullable=False)
    user_full_name = Column(String, nullable=False)
    delivery_type_id = Column(SmallInteger, ForeignKey("delivery_types.id"))
    payment_state_id = Column(SmallInteger, ForeignKey("payment_state.id"))
    total_amount = Column(Numeric(10, 2))
    delivery_address = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), primary_key=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    order = relationship("Order", back_populates="items")

class OrderFeedback(Base):
    __tablename__ = "order_feedback"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    description = Column(String)
    score = Column(SmallInteger, nullable=False) # 1-5
    created_at = Column(DateTime(timezone=True), server_default=func.now())
