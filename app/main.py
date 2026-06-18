from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import products, categories, orders, testimonials, faqs, contact, custom_orders, auth
from app.core.config import settings
from app.db.database import engine, SessionLocal
from app.models import base

base.Base.metadata.create_all(bind=engine)

app = FastAPI(title="New Face Furniture API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://newfacefurniture.co.ke",
        "https://www.newfacefurniture.co.ke",
    ],
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


@app.get("/seed-categories")
def seed_categories():
    from app.models.base import Category
    db = SessionLocal()
    try:
        existing = db.query(Category).count()
        if existing > 0:
            return {"message": f"Already have {existing} categories, skipping"}
        categories_data = [
            Category(name='Sofas & Seating', slug='sofas-seating'),
            Category(name='Beds & Bedroom', slug='beds-bedroom'),
            Category(name='Dining Sets', slug='dining-sets'),
            Category(name='Coffee Tables', slug='coffee-tables'),
            Category(name='TV Stands', slug='tv-stands'),
            Category(name='Wardrobes', slug='wardrobes'),
            Category(name='Office Furniture', slug='office-furniture'),
            Category(name='Accent Chairs', slug='accent-chairs'),
            Category(name='Outdoor Furniture', slug='outdoor-furniture'),
            Category(name='Storage Solutions', slug='storage-solutions'),
            Category(name='Hotel & Restaurant', slug='hotel-restaurant'),
            Category(name='Airbnb Furnishing', slug='airbnb-furnishing'),
            Category(name='Lounges', slug='lounges'),
            Category(name='Bar Stools', slug='bar-stools'),
            Category(name='Custom', slug='custom'),
        ]
        db.add_all(categories_data)
        db.commit()
        return {"message": "Categories seeded successfully!", "count": len(categories_data)}
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()