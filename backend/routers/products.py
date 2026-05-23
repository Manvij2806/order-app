from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("", response_model=List[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products

def seed_products(db: Session):
    if db.query(models.Product).count() == 0:
        sample_products = [
            models.Product(name="Wireless Mouse", price=29.99, stock_qty=150),
            models.Product(name="Mechanical Keyboard", price=89.99, stock_qty=50),
            models.Product(name="27-inch Monitor", price=199.99, stock_qty=30),
            models.Product(name="USB-C Hub", price=19.99, stock_qty=200),
            models.Product(name="Noise Cancelling Headphones", price=149.99, stock_qty=45),
            models.Product(name="Laptop Stand", price=34.99, stock_qty=80),
            models.Product(name="Webcam 1080p", price=59.99, stock_qty=60),
            models.Product(name="Mouse Pad", price=14.99, stock_qty=300),
        ]
        db.add_all(sample_products)
        db.commit()
