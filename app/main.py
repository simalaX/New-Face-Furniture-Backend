from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import products, categories, orders, testimonials, faqs, contact, custom_orders, auth
from app.core.config import settings
from app.db.database import engine
from app.models import base

base.Base.metadata.create_all(bind=engine)

app = FastAPI(title="New Face Furniture API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(testimonials.router, prefix="/api/v1/testimonials", tags=["testimonials"])
app.include_router(faqs.router, prefix="/api/v1/faqs", tags=["faqs"])
app.include_router(contact.router, prefix="/api/v1/contact", tags=["contact"])
app.include_router(custom_orders.router, prefix="/api/v1/custom-orders", tags=["custom-orders"])

@app.get("/")
def root():
    return {"message": "New Face Furniture API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}