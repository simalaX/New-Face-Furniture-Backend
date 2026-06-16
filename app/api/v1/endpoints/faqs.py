from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.base import FAQ
from app.schemas.schemas import FAQCreate, FAQOut

router = APIRouter()

@router.get("/", response_model=List[FAQOut])
def get_faqs(db: Session = Depends(get_db)):
    return db.query(FAQ).order_by(FAQ.order).all()

@router.post("/", response_model=FAQOut)
def create_faq(faq: FAQCreate, db: Session = Depends(get_db)):
    db_faq = FAQ(**faq.model_dump())
    db.add(db_faq)
    db.commit()
    db.refresh(db_faq)
    return db_faq

@router.put("/{fid}", response_model=FAQOut)
def update_faq(fid: int, faq: FAQCreate, db: Session = Depends(get_db)):
    db_faq = db.query(FAQ).filter(FAQ.id == fid).first()
    if not db_faq:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in faq.model_dump().items():
        setattr(db_faq, k, v)
    db.commit()
    db.refresh(db_faq)
    return db_faq

@router.delete("/{fid}")
def delete_faq(fid: int, db: Session = Depends(get_db)):
    db_faq = db.query(FAQ).filter(FAQ.id == fid).first()
    if not db_faq:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_faq)
    db.commit()
    return {"message": "Deleted"}
