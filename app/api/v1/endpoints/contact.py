from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.base import ContactMessage
from app.schemas.schemas import ContactCreate, ContactOut

router = APIRouter()

@router.get("/", response_model=List[ContactOut])
def get_messages(db: Session = Depends(get_db)):
    return db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).all()

@router.post("/", response_model=ContactOut)
def send_message(msg: ContactCreate, db: Session = Depends(get_db)):
    db_msg = ContactMessage(**msg.model_dump())
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg

@router.put("/{mid}/read")
def mark_read(mid: int, db: Session = Depends(get_db)):
    msg = db.query(ContactMessage).filter(ContactMessage.id == mid).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Not found")
    msg.is_read = True
    db.commit()
    return {"message": "Marked as read"}
