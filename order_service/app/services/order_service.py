from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import date, datetime
from app import models, schemas
from uuid import UUID
import uuid
import random
import os
import requests
from fastapi import HTTPException


class OrderService:
    @staticmethod
    def create_order(db: Session, order_data: schemas.OrderCreate) -> models.Order:
        # 1. Generate unique order number
        while True:
            order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            if not db.query(models.Order).filter(models.Order.order_number == order_number).first():
                break

        # Calculate total and create items
        total_amount = 0

        # Create order record
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

        CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://catalog-service:8080/catalog")

        reserved_items = []

        try:
            for item in order_data.items:
                # 1. Check availability and get product price
                # First get product details for the price
                product_response = requests.get(f"{CATALOG_SERVICE_URL}/products/{item.product_id}", timeout=5)
                if product_response.status_code == 404:
                    raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
                product_response.raise_for_status()
                product_data = product_response.json()

                # Check availability
                avail_response = requests.get(
                    f"{CATALOG_SERVICE_URL}/products/{item.product_id}/availability?quantity={item.quantity}",
                    timeout=5)
                avail_response.raise_for_status()
                avail_data = avail_response.json()

                if not avail_data.get("available"):
                    raise HTTPException(status_code=400, detail=f"Insufficient stock for product {item.product_id}")

                # 2. Update stock using SUBTRACT
                stock_response = requests.patch(
                    f"{CATALOG_SERVICE_URL}/products/{item.product_id}/stock",
                    json={"quantity": item.quantity, "operation": "SUBTRACT"},
                    timeout=5
                )
                if stock_response.status_code == 400:
                    raise HTTPException(status_code=400,
                                        detail=f"Insufficient stock for product {item.product_id} during reservation")
                stock_response.raise_for_status()

                # Track successfully reserved items for compensation
                reserved_items.append(item)

                # Get actual price from product
                item_price = float(product_data.get("price", 0))
                total_amount += item_price * item.quantity

                # Create order item
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

        except Exception as e:
            # Rollback database
            db.rollback()
            # Compensate reserved items in catalog-service
            for res_item in reserved_items:
                try:
                    requests.patch(
                        f"{CATALOG_SERVICE_URL}/products/{res_item.product_id}/stock",
                        json={"quantity": res_item.quantity, "operation": "ADD"},
                        timeout=5
                    )
                except Exception as comp_e:
                    # In a real system, you would log this to a dead letter queue or alerting system
                    print(f"CRITICAL: Failed to compensate stock for {res_item.product_id}: {comp_e}")

            if isinstance(e, HTTPException):
                raise e
            if isinstance(e, requests.RequestException):
                raise HTTPException(status_code=503, detail=f"Catalog service unavailable: {str(e)}")
            raise e

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

        # If rejecting order, return stock
        if order_state_id == 5 and order.order_state_id != 5:
            CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://catalog-service:8080/catalog")
            for item in order.items:
                try:
                    requests.patch(
                        f"{CATALOG_SERVICE_URL}/products/{item.product_id}/stock",
                        json={"quantity": item.quantity, "operation": "ADD"},
                        timeout=5
                    )
                except requests.RequestException as e:
                    print(f"Failed to refund stock for product {item.product_id} from order {order_id}: {e}")
                    # Could log these failures for manual compensation.

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
