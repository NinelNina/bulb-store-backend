from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..database import get_db
from .. import schemas
from ..services.order_service import OrderService
from uuid import UUID

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", response_model=schemas.Order, status_code=201)
def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
    return OrderService.create_order(db, order_data)

@router.get("/delivery-types", response_model=List[schemas.ReferenceData])
def get_delivery_types(db: Session = Depends(get_db)):
    return OrderService.get_delivery_types(db)

@router.get("/statuses", response_model=List[schemas.ReferenceData])
def get_order_statuses(db: Session = Depends(get_db)):
    return OrderService.get_order_statuses(db)

@router.get("/payment-statuses", response_model=List[schemas.ReferenceData])
def get_payment_statuses(db: Session = Depends(get_db)):
    return OrderService.get_payment_statuses(db)

@router.get("/tracking", response_model=schemas.OrderTracking)
def track_order(orderNumber: str, phoneNumber: str, db: Session = Depends(get_db)):
    return OrderService.track_order(db, orderNumber, phoneNumber)

@router.get("/{orderId}/tracking", response_model=schemas.OrderTracking)
def track_order_by_id(orderId: UUID, db: Session = Depends(get_db)):
    return OrderService.track_order_by_id(db, orderId)

@router.get("", response_model=List[schemas.Order])
def list_orders(
    page: int = 1,
    size: int = 20,
    orderStateId: Optional[int] = None,
    paymentStateId: Optional[int] = None,
    createdAtFrom: Optional[date] = None,
    createdAtTo: Optional[date] = None,
    createdAt: Optional[date] = None,
    db: Session = Depends(get_db)
):
    filters = {
        "orderStateId": orderStateId,
        "paymentStateId": paymentStateId,
        "createdAtFrom": createdAtFrom,
        "createdAtTo": createdAtTo,
        "createdAt": createdAt
    }
    return OrderService.list_orders(db, page, size, filters)

@router.patch("/{orderId}/status", response_model=schemas.Order)
def update_order_status(orderId: UUID, status_data: dict, db: Session = Depends(get_db)):
    return OrderService.update_order_status(db, orderId, status_data.get("orderStateId"))

@router.patch("/{orderId}/payment", response_model=schemas.Order)
def update_payment_status(orderId: UUID, payment_data: dict, db: Session = Depends(get_db)):
    return OrderService.update_payment_status(db, orderId, payment_data.get("paymentStateId"))

@router.post("/{orderId}/feedback", status_code=201)
def submit_feedback(orderId: UUID, feedback_data: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    return OrderService.submit_feedback(db, orderId, feedback_data)
