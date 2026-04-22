from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    model_config = ConfigDict(from_attributes=True)

class ProductBase(BaseModel):
    name: str
    socket: str
    power: int
    color_temperature: int
    brightness: int
    shape: Optional[str] = None
    description: Optional[str] = None
    price: Decimal
    quantity: int = 0
    category_id: UUID

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    socket: Optional[str] = None
    power: Optional[int] = None
    color_temperature: Optional[int] = None
    brightness: Optional[int] = None
    shape: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    quantity: Optional[int] = None
    category_id: Optional[UUID] = None

class Product(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    model_config = ConfigDict(from_attributes=True)
