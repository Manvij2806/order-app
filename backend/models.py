from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    orders = relationship("Order", back_populates="user")

class OrderStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    delivered = "delivered"
    cancelled = "cancelled"

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    stock_qty = Column(Integer)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    customer_name = Column(String)
    customer_email = Column(String, index=True)
    delivery_address = Column(String)
    phone = Column(String)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    qty = Column(Integer)
    price_at_order = Column(Float)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
