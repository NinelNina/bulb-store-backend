from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

class OrderItemBase(BaseModel):
    product_id: UUID
    quantity: int
    price: Decimal

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class OrderBase(BaseModel):
    phone_number: str
    user_full_name: str
    delivery_type_id: int
    delivery_address: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class Order(OrderBase):
    id: UUID
    order_number: str
    order_state_id: int
    payment_state_id: int
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    model_config = ConfigDict(from_attributes=True)
    
class OrderTracking(Order):
    status_name: str

class ReferenceData(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class FeedbackCreate(BaseModel):
    productId: UUID
    description: str
    score: int
