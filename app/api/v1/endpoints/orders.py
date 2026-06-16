from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import random, string
from app.db.database import get_db
from app.models.base import Order, OrderItem
from app.schemas.schemas import OrderCreate, OrderOut

router = APIRouter()

def generate_order_number():
    return "TF-" + "".join(random.choices(string.digits, k=6))

@router.get("/", response_model=List[OrderOut])
def get_orders(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/", response_model=OrderOut)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    items_data = order.items
    order_data = order.model_dump(exclude={"items"})
    order_data["order_number"] = generate_order_number()
    db_order = Order(**order_data)
    db.add(db_order)
    db.flush()
    for item in items_data:
        db_item = OrderItem(order_id=db_order.id, **item.model_dump())
        db.add(db_item)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.put("/{order_id}/status")
def update_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    db.commit()
    return {"message": "Status updated", "status": status}

@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return {"message": "Order deleted"}
