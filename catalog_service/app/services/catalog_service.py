from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from uuid import UUID
from app import models, schemas
from fastapi import HTTPException


class CatalogService:
    @staticmethod
    def get_products(
            db: Session,
            page: int = 1,
            size: int = 20,
            category_id: Optional[UUID] = None
    ) -> List[models.Product]:
        query = db.query(models.Product).filter(models.Product.is_deleted == False)
        if category_id:
            query = query.filter(models.Product.category_id == category_id)
        return query.order_by(models.Product.created_at.desc()).offset((page - 1) * size).limit(size).all()

    @staticmethod
    def search_products(
            db: Session,
            params: dict,
            page: int = 1,
            size: int = 20
    ) -> List[models.Product]:
        query = db.query(models.Product).filter(models.Product.is_deleted == False)

        q = params.get("q")
        if q:
            query = query.filter(or_(models.Product.name.ilike(f"%{q}%"), models.Product.description.ilike(f"%{q}%")))

        if params.get("categoryId"):
            query = query.filter(models.Product.category_id == params.get("categoryId"))
        if params.get("socket"):
            query = query.filter(models.Product.socket == params.get("socket"))
        if params.get("minPower"):
            query = query.filter(models.Product.power >= params.get("minPower"))
        if params.get("maxPower"):
            query = query.filter(models.Product.power <= params.get("maxPower"))
        if params.get("minBrightness"):
            query = query.filter(models.Product.brightness >= params.get("minBrightness"))
        if params.get("maxBrightness"):
            query = query.filter(models.Product.brightness <= params.get("maxBrightness"))
        if params.get("colorTemperature"):
            query = query.filter(models.Product.color_temperature == params.get("colorTemperature"))
        if params.get("shape"):
            query = query.filter(models.Product.shape == params.get("shape"))
        if params.get("minPrice"):
            query = query.filter(models.Product.price >= params.get("minPrice"))
        if params.get("maxPrice"):
            query = query.filter(models.Product.price <= params.get("maxPrice"))

        sort = params.get("sort")
        if sort == "price_asc":
            query = query.order_by(models.Product.price.asc())
        elif sort == "price_desc":
            query = query.order_by(models.Product.price.desc())
        elif sort == "name_asc":
            query = query.order_by(models.Product.name.asc())
        else:
            query = query.order_by(models.Product.created_at.desc())

        return query.offset((page - 1) * size).limit(size).all()

    @staticmethod
    def get_low_stock(db: Session, threshold: int = 10) -> List[models.Product]:
        return db.query(models.Product).filter(
            models.Product.quantity <= threshold,
            models.Product.is_deleted == False
        ).all()

    @staticmethod
    def get_product(db: Session, product_id: UUID) -> models.Product:
        product = db.query(models.Product).filter(
            models.Product.id == product_id,
            models.Product.is_deleted == False
        ).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    @staticmethod
    def check_availability(db: Session, product_id: UUID, quantity: int = 1) -> dict:
        product = CatalogService.get_product(db, product_id)
        return {
            "productId": product_id,
            "available": product.quantity >= quantity,
            "requested": quantity,
            "current": product.quantity
        }

    @staticmethod
    def create_product(db: Session, product_data: schemas.ProductCreate) -> models.Product:
        db_product = models.Product(**product_data.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def update_product(db: Session, product_id: UUID, update_data: schemas.ProductUpdate) -> models.Product:
        db_product = CatalogService.get_product(db, product_id)
        data = update_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def update_stock(db: Session, product_id: UUID, stock_data: dict) -> models.Product:
        db_product = CatalogService.get_product(db, product_id)
        quantity = stock_data.get("quantity", 0)
        operation = stock_data.get("operation", "SET")

        if operation == "SET":
            db_product.quantity = quantity
        elif operation == "ADD":
            db_product.quantity += quantity
        elif operation == "SUBTRACT":
            if db_product.quantity < quantity:
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="Insufficient stock")
            db_product.quantity -= quantity

        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def delete_product(db: Session, product_id: UUID) -> dict:
        db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        db_product.is_deleted = True
        db.commit()
        return {"message": "Product deleted"}


class CategoryService:
    @staticmethod
    def get_categories(db: Session) -> List[models.Category]:
        return db.query(models.Category).filter(
            models.Category.is_deleted == False
        ).order_by(models.Category.name).all()

    @staticmethod
    def create_category(db: Session, category_data: schemas.CategoryCreate) -> models.Category:
        db_category = models.Category(**category_data.model_dump())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def update_category(db: Session, category_id: UUID, category_data: schemas.CategoryCreate) -> models.Category:
        db_category = db.query(models.Category).filter(
            models.Category.id == category_id,
            models.Category.is_deleted == False
        ).first()
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        db_category.name = category_data.name
        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def delete_category(db: Session, category_id: UUID) -> dict:
        db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        db_category.is_deleted = True
        db.commit()
        return {"message": "Category deleted"}
