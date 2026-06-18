from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.base import Product
from app.schemas.schemas import ProductCreate, ProductOut
from app.core.auth import get_current_admin   # ← import your auth dependency

router = APIRouter()


@router.get("/", response_model=List[ProductOut])
def get_products(
    skip: int = 0,
    limit: int = 20,
    category_id: Optional[int] = None,
    featured: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if featured is not None:
        query = query.filter(Product.is_featured == featured)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()


# ── IMPORTANT: /slug/{slug} must come BEFORE /{product_id} ──────────────────
@router.get("/slug/{slug}", response_model=ProductOut)
def get_product_by_slug(slug: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.slug == slug).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductOut)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),   # ← auth guard
):
    # Extra safety: reject if category_id is somehow missing
    if not product.category_id:
        raise HTTPException(status_code=422, detail="category_id is required")

    # Prevent duplicate slugs
    existing = db.query(Product).filter(Product.slug == product.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Slug '{product.slug}' already exists")

    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),   # ← auth guard
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Allow slug to stay the same on update; only block if taken by a *different* product
    existing = db.query(Product).filter(
        Product.slug == product.slug,
        Product.id != product_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Slug '{product.slug}' already taken")

    for key, value in product.model_dump().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),   # ← auth guard
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted"}