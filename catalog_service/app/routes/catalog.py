from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import schemas
from ..services.catalog_service import CatalogService, CategoryService
from uuid import UUID

router = APIRouter(prefix="/catalog", tags=["catalog"])

@router.get("/products", response_model=List[schemas.Product])
def get_products(
    page: int = 1, 
    size: int = 20, 
    categoryId: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    return CatalogService.get_products(db, page, size, categoryId)

@router.get("/products/search", response_model=List[schemas.Product])
def search_products(
    q: Optional[str] = None,
    categoryId: Optional[UUID] = None,
    socket: Optional[str] = None,
    minPower: Optional[int] = None,
    maxPower: Optional[int] = None,
    minBrightness: Optional[int] = None,
    maxBrightness: Optional[int] = None,
    colorTemperature: Optional[int] = None,
    shape: Optional[str] = None,
    minPrice: Optional[float] = None,
    maxPrice: Optional[float] = None,
    sort: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db)
):
    params = {
        "q": q, "categoryId": categoryId, "socket": socket,
        "minPower": minPower, "maxPower": maxPower,
        "minBrightness": minBrightness, "maxBrightness": maxBrightness,
        "colorTemperature": colorTemperature, "shape": shape,
        "minPrice": minPrice, "maxPrice": maxPrice, "sort": sort
    }
    return CatalogService.search_products(db, params, page, size)

@router.get("/products/low-stock", response_model=List[schemas.Product])
def get_low_stock(threshold: int = 10, db: Session = Depends(get_db)):
    return CatalogService.get_low_stock(db, threshold)

@router.get("/products/{productId}", response_model=schemas.Product)
def get_product(productId: UUID, db: Session = Depends(get_db)):
    return CatalogService.get_product(db, productId)

@router.get("/products/{productId}/availability")
def check_availability(productId: UUID, quantity: int = 1, db: Session = Depends(get_db)):
    return CatalogService.check_availability(db, productId, quantity)

@router.post("/products", response_model=schemas.Product, status_code=201)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return CatalogService.create_product(db, product)

@router.patch("/products/{productId}", response_model=schemas.Product)
def update_product(productId: UUID, product_update: schemas.ProductUpdate, db: Session = Depends(get_db)):
    return CatalogService.update_product(db, productId, product_update)

@router.patch("/products/{productId}/stock")
def update_product_stock(productId: UUID, stock_data: dict, db: Session = Depends(get_db)):
    return CatalogService.update_stock(db, productId, stock_data)

@router.delete("/products/{productId}")
def delete_product(productId: UUID, db: Session = Depends(get_db)):
    return CatalogService.delete_product(db, productId)

# Categories
@router.get("/categories", response_model=List[schemas.Category])
def get_categories(db: Session = Depends(get_db)):
    return CategoryService.get_categories(db)

@router.post("/categories", response_model=schemas.Category, status_code=201)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return CategoryService.create_category(db, category)

@router.patch("/categories/{categoryId}", response_model=schemas.Category)
def update_category(categoryId: UUID, category_update: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return CategoryService.update_category(db, categoryId, category_update)

@router.delete("/categories/{categoryId}")
def delete_category(categoryId: UUID, db: Session = Depends(get_db)):
    return CategoryService.delete_category(db, categoryId)
