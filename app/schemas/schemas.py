from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Union, Any
from datetime import datetime

# Category schemas
class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# Product schemas
class ProductBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    images: Optional[List[str]] = []
    dimensions: Optional[str] = None
    materials: Optional[str] = None
    is_featured: bool = False
    in_stock: bool = True
    category_id: int

    @field_validator("images", mode="before")
    @classmethod
    def normalize_images(cls, value: Any) -> List[str]:
        """
        Accepts either:
          - a list of plain URL strings: ["https://..."]
          - a list of Cloudinary-style objects: [{"secure_url": "https://...", "public_id": "..."}]
          - a mix of both
        and always normalizes to a list of plain URL strings.
        """
        if value is None:
            return []
        normalized: List[str] = []
        for item in value:
            if isinstance(item, str):
                normalized.append(item)
            elif isinstance(item, dict):
                url = item.get("secure_url") or item.get("url") or item.get("image_url")
                if url:
                    normalized.append(url)
            # silently skip anything else unrecognized (e.g. None)
        return normalized

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    category: Optional[CategoryOut] = None
    created_at: datetime
    class Config:
        from_attributes = True

# Order schemas
class OrderItemCreate(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float

class OrderCreate(BaseModel):
    full_name: str
    phone: str
    email: Optional[str] = None
    county: str
    town: str
    address: str
    notes: Optional[str] = None
    payment_method: str
    subtotal: float
    delivery_fee: float = 0
    total: float
    items: List[OrderItemCreate]

class OrderOut(BaseModel):
    id: int
    order_number: str
    full_name: str
    phone: str
    status: str
    total: float
    created_at: datetime
    class Config:
        from_attributes = True

# Testimonial schemas
class TestimonialCreate(BaseModel):
    customer_name: str
    rating: int
    review: str
    location: Optional[str] = None

class TestimonialOut(TestimonialCreate):
    id: int
    is_approved: bool
    created_at: datetime
    class Config:
        from_attributes = True

# FAQ schemas
class FAQCreate(BaseModel):
    question: str
    answer: str
    order: int = 0

class FAQOut(FAQCreate):
    id: int
    class Config:
        from_attributes = True

# Contact schemas
class ContactCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    message: str

class ContactOut(ContactCreate):
    id: int
    is_read: bool
    created_at: datetime
    class Config:
        from_attributes = True

# Custom Order schemas
class CustomOrderCreate(BaseModel):
    customer_name: str
    phone: str
    email: Optional[str] = None
    furniture_type: str
    dimensions: Optional[str] = None
    materials: Optional[str] = None
    description: str
    reference_images: Optional[List[str]] = []
    budget: Optional[str] = None

class CustomOrderOut(CustomOrderCreate):
    id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True