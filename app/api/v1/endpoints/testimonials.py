from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.base import Testimonial
from app.schemas.schemas import TestimonialCreate, TestimonialOut

router = APIRouter()

@router.get("/", response_model=List[TestimonialOut])
def get_testimonials(approved_only: bool = True, db: Session = Depends(get_db)):
    q = db.query(Testimonial)
    if approved_only:
        q = q.filter(Testimonial.is_approved == True)
    return q.order_by(Testimonial.created_at.desc()).all()

@router.post("/", response_model=TestimonialOut)
def create_testimonial(t: TestimonialCreate, db: Session = Depends(get_db)):
    db_t = Testimonial(**t.model_dump())
    db.add(db_t)
    db.commit()
    db.refresh(db_t)
    return db_t

@router.put("/{tid}/approve")
def approve(tid: int, db: Session = Depends(get_db)):
    t = db.query(Testimonial).filter(Testimonial.id == tid).first()
    if not t:
        raise HTTPException(status_code=404, detail="Not found")
    t.is_approved = True
    db.commit()
    return {"message": "Approved"}

@router.delete("/{tid}")
def delete(tid: int, db: Session = Depends(get_db)):
    t = db.query(Testimonial).filter(Testimonial.id == tid).first()
    if not t:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(t)
    db.commit()
    return {"message": "Deleted"}
