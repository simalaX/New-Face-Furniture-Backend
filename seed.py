from app.db.database import SessionLocal 
from app.models.base import Category 
db = SessionLocal() 
cats = [Category(name='Sofas',slug='sofas'),Category(name='Beds',slug='beds'),Category(name='Dining Sets',slug='dining-sets'),Category(name='Coffee Tables',slug='coffee-tables'),Category(name='TV Stands',slug='tv-stands'),Category(name='Wardrobes',slug='wardrobes'),Category(name='Office',slug='office'),Category(name='Custom',slug='custom')] 
db.add_all(cats) 
db.commit() 
db.close() 
print('Done') 
