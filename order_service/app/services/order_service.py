from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import date, datetime
from app import models, schemas
from uuid import UUID
import uuid
import random
from fastapi import HTTPException


class OrderService:
    @staticmethod
    def create_order(db: Session, order_data: schemas.OrderCreate) -> models.Order:
        while True:
            order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            if not db.query(models.Order).filter(models.Order.order_number == order_number).first():
                break

        total_amount = 0

        db_order = models.Order(
            order_number=order_number,
            order_state_id=1,  # IN_PROCESS
            phone_number=order_data.phone_number,
            user_full_name=order_data.user_full_name,
            delivery_type_id=order_data.delivery_type_id,
            payment_state_id=1,  # PENDING
            total_amount=0,
            delivery_address=order_data.delivery_address
        )
        db.add(db_order)
        db.flush()

        for item in order_data.items:
            product = db.query(models.Product).filter(models.Product.id == item.product_id).with_for_update().first()
            if not product:
                db.rollback()
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            if product.quantity < item.quantity:
                db.rollback()
                raise HTTPException(status_code=400, detail=f"Insufficient stock for product {item.product_id}")

            product.quantity -= item.quantity

            item_price = product.price if product.price is not None else 0
            total_amount += item_price * item.quantity

            db_item = models.OrderItem(
                order_id=db_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item_price
            )
            db.add(db_item)

        db_order.total_amount = total_amount
        db.commit()
        db.refresh(db_order)
        return db_order

    @staticmethod
    def get_delivery_types(db: Session) -> List[models.DeliveryType]:
        return db.query(models.DeliveryType).all()

    @staticmethod
    def get_order_statuses(db: Session) -> List[models.OrderState]:
        return db.query(models.OrderState).all()

    @staticmethod
    def get_payment_statuses(db: Session) -> List[models.PaymentState]:
        return db.query(models.PaymentState).all()

    @staticmethod
    def track_order(db: Session, order_number: Optional[str] = None, phone_number: Optional[str] = None) -> dict:
        if not order_number and not phone_number:
            raise HTTPException(status_code=400, detail="Must provide orderNumber or phoneNumber")

        conditions = []
        if order_number:
            conditions.append(models.Order.order_number == order_number)
        if phone_number:
            phone_number = phone_number.replace(" ", "+")
            conditions.append(models.Order.phone_number == phone_number)

        order = db.query(models.Order).filter(or_(*conditions)).order_by(models.Order.created_at.desc()).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        status = db.query(models.OrderState).filter(models.OrderState.id == order.order_state_id).first()
        order_dict = schemas.Order.model_validate(order).model_dump()
        order_dict["status_name"] = status.name if status else "UNKNOWN"
        return order_dict

    @staticmethod
    def track_order_by_id(db: Session, order_id: UUID) -> dict:
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        status = db.query(models.OrderState).filter(models.OrderState.id == order.order_state_id).first()
        order_dict = schemas.Order.model_validate(order).model_dump()
        order_dict["status_name"] = status.name if status else "UNKNOWN"
        return order_dict

    @staticmethod
    def list_orders(
            db: Session,
            page: int = 1,
            size: int = 20,
            filters: dict = {}
    ) -> List[models.Order]:
        query = db.query(models.Order).filter(models.Order.is_deleted == False)

        if filters.get("orderStateId"):
            query = query.filter(models.Order.order_state_id == filters["orderStateId"])
        if filters.get("paymentStateId"):
            query = query.filter(models.Order.payment_state_id == filters["paymentStateId"])
        if filters.get("createdAtFrom"):
            query = query.filter(
                models.Order.created_at >= datetime.combine(filters["createdAtFrom"], datetime.min.time()))
        if filters.get("createdAtTo"):
            query = query.filter(
                models.Order.created_at <= datetime.combine(filters["createdAtTo"], datetime.max.time()))
        if filters.get("createdAt"):
            query = query.filter(func.date(models.Order.created_at) == filters["createdAt"])

        return query.order_by(models.Order.created_at.desc()).offset((page - 1) * size).limit(size).all()

    @staticmethod
    def update_order_status(db: Session, order_id: UUID, order_state_id: int) -> models.Order:
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        order.order_state_id = order_state_id
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def update_payment_status(db: Session, order_id: UUID, payment_state_id: int) -> models.Order:
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        order.payment_state_id = payment_state_id
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def submit_feedback(db: Session, order_id: UUID, feedback_data: schemas.FeedbackCreate) -> dict:
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        db_feedback = models.OrderFeedback(
            order_id=order_id,
            product_id=feedback_data.productId,
            description=feedback_data.description,
            score=feedback_data.score
        )
        db.add(db_feedback)
        db.commit()
        return {"message": "Feedback submitted successfully"}
