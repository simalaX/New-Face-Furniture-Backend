from app.db.database import SessionLocal
from app.models.base import Category

db = SessionLocal()

# Delete existing categories if you want to replace them (optional)
# db.query(Category).delete()

cats = [
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

db.add_all(cats)
db.commit()
db.close()
print('Categories seeded successfully!')