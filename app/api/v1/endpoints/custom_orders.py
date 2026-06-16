from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import cloudinary
import cloudinary.uploader
from app.db.database import get_db
from app.models.base import CustomOrder
from app.schemas.schemas import CustomOrderCreate, CustomOrderOut
from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

router = APIRouter()

@router.get("/", response_model=List[CustomOrderOut])
def get_custom_orders(db: Session = Depends(get_db)):
    return db.query(CustomOrder).order_by(CustomOrder.created_at.desc()).all()

@router.get("/{cid}", response_model=CustomOrderOut)
def get_custom_order(cid: int, db: Session = Depends(get_db)):
    co = db.query(CustomOrder).filter(CustomOrder.id == cid).first()
    if not co:
        raise HTTPException(status_code=404, detail="Not found")
    return co

@router.post("/", response_model=CustomOrderOut)
def create_custom_order(order: CustomOrderCreate, db: Session = Depends(get_db)):
    db_order = CustomOrder(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    result = cloudinary.uploader.upload(
        contents,
        folder="tangerine/custom-orders",
        transformation=[{"quality": "auto", "fetch_format": "auto"}]
    )
    return {"url": result["secure_url"], "public_id": result["public_id"]}

@router.post("/upload-product-image")
async def upload_product_image(file: UploadFile = File(...)):
    contents = await file.read()
    result = cloudinary.uploader.upload(
        contents,
        folder="tangerine/products",
        transformation=[{"quality": "auto", "fetch_format": "auto", "width": 800, "crop": "limit"}]
    )
    return {"url": result["secure_url"], "public_id": result["public_id"]}

@router.put("/{cid}/status")
def update_status(cid: int, status: str, db: Session = Depends(get_db)):
    co = db.query(CustomOrder).filter(CustomOrder.id == cid).first()
    if not co:
        raise HTTPException(status_code=404, detail="Not found")
    co.status = status
    db.commit()
    return {"message": "Updated"}
