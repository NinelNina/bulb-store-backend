from sqlalchemy.orm import Session
from app import models


def seed_order_data(db: Session):
    states = [
        (1, 'IN_PROCESS', 'Обрабатывается'),
        (2, 'IN_TRANSIT', 'В пути'),
        (3, 'DELIVERED', 'Доставлено на объект'),
        (4, 'RECEIVED', 'Получено клиентом'),
        (5, 'REJECTED', 'Отклонено')
    ]
    for id, name, desc in states:
        if not db.query(models.OrderState).filter(models.OrderState.id == id).first():
            db.add(models.OrderState(id=id, name=name, description=desc))

    payments = [
        (1, 'PENDING', 'Ожидает оплаты'),
        (2, 'PAID', 'Оплачено'),
        (3, 'REFUNDED', 'Возврат'),
        (4, 'CANCELLED', 'Отменено')
    ]
    for id, name, desc in payments:
        if not db.query(models.PaymentState).filter(models.PaymentState.id == id).first():
            db.add(models.PaymentState(id=id, name=name, description=desc))

    deliveries = [
        (1, 'CDEK', 'СДЭК'),
        (2, 'YANDEX', 'Яндекс Доставка'),
        (3, 'POST', 'Почта России'),
        (4, 'BOXBERRY', 'Boxberry'),
        (5, 'САМОВЫВОЗ', 'Самовывоз')
    ]
    for id, name, desc in deliveries:
        if not db.query(models.DeliveryType).filter(models.DeliveryType.id == id).first():
            db.add(models.DeliveryType(id=id, name=name, description=desc))

    db.commit()
    print("Order reference data seeded.")

    if not db.query(models.Order).first():
        products = db.query(models.Product).limit(3).all()
        if len(products) > 0:
            order1 = models.Order(
                order_number="ORD-0001",
                order_state_id=1,
                phone_number="+79998887766",
                user_full_name="Иван Иванов",
                delivery_type_id=1,
                payment_state_id=1,
                total_amount=0,
                delivery_address="г. Москва, ул. Пушкина, д. 10, кв. 5"
            )
            db.add(order1)
            db.flush()

            total = 0
            for prod in products:
                qty = 2
                price = prod.price if prod.price else 500.0
                item = models.OrderItem(
                    order_id=order1.id,
                    product_id=prod.id,
                    quantity=qty,
                    price=price
                )
                db.add(item)
                total += qty * price

            order1.total_amount = total

            order2 = models.Order(
                order_number="ORD-0002",
                order_state_id=3,
                phone_number="+79991112233",
                user_full_name="Петр Петров",
                delivery_type_id=2,
                payment_state_id=2,
                total_amount=0,
                delivery_address="г. Санкт-Петербург, Невский пр., д. 1, кв. 1"
            )
            db.add(order2)
            db.flush()

            prod = products[0]
            qty2 = 1
            price2 = prod.price if prod.price else 500.0
            item2 = models.OrderItem(
                order_id=order2.id,
                product_id=prod.id,
                quantity=qty2,
                price=price2
            )
            db.add(item2)
            order2.total_amount = qty2 * price2

            db.commit()
            print("Test orders seeded.")
