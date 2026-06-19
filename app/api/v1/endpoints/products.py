from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.base import Product
from app.schemas.schemas import ProductCreate, ProductOut

router = APIRouter()


def make_unique_slug(db: Session, base_slug: str, exclude_id: Optional[int] = None) -> str:
    """
    Returns a slug guaranteed to be unique among products.
    If base_slug is taken, appends -2, -3, -4... until a free one is found.
    exclude_id lets an update check ignore the product's own current row.
    """
    slug = base_slug
    counter = 2
    while True:
        query = db.query(Product).filter(Product.slug == slug)
        if exclude_id is not None:
            query = query.filter(Product.id != exclude_id)
        if not query.first():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


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


# ── /slug/{slug} must come BEFORE /{product_id} ──────────────────────────────
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
):
    if not product.category_id:
        raise HTTPException(status_code=422, detail="category_id is required")

    data = product.model_dump()
    data["slug"] = make_unique_slug(db, data["slug"])

    db_product = Product(**data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    data = product.model_dump()
    data["slug"] = make_unique_slug(db, data["slug"], exclude_id=product_id)

    for key, value in data.items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted"}