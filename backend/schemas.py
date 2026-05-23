from pydantic import BaseModel, EmailStr, Field
from typing import List
from datetime import datetime
from models import OrderStatus

class OrderItemCreate(BaseModel):
    product_id: int
    qty: int = Field(gt=0)

class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=3)
    customer_email: EmailStr
    delivery_address: str = Field(min_length=5)
    phone: str = Field(pattern=r"^\d{10}$")
    items: List[OrderItemCreate] = Field(min_length=1)

class OrderItemDetailResponse(BaseModel):
    product_name: str
    qty: int
    price_at_order: float

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    delivery_address: str
    phone: str
    status: OrderStatus
    created_at: datetime
    total: float
    items: List[OrderItemDetailResponse]
    
    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock_qty: int
    
    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
