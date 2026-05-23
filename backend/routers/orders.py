from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from routers.auth import get_current_user
import models
import schemas

router = APIRouter(prefix="/api/orders", tags=["Cart"])

@router.post("", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_in: schemas.OrderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    total = 0.0
    order_items_models = []
    
    for item_in in order_in.items:
        product = db.query(models.Product).filter(models.Product.id == item_in.product_id).first()
        if not product:
            raise HTTPException(status_code=422, detail=f"Product with id {item_in.product_id} not found")
        
        if product.stock_qty < item_in.qty:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Insufficient stock for product {product.name}")
        
        product.stock_qty -= item_in.qty
        
        price = product.price
        total += price * item_in.qty
        
        order_item = models.OrderItem(
            product_id=product.id,
            qty=item_in.qty,
            price_at_order=price
        )
        order_items_models.append(order_item)
        
    new_order = models.Order(
        user_id=current_user.id,
        customer_name=order_in.customer_name,
        customer_email=order_in.customer_email,
        delivery_address=order_in.delivery_address,
        phone=order_in.phone,
        status=models.OrderStatus.pending,
    )
    
    db.add(new_order)
    db.flush()
    
    for oi in order_items_models:
        oi.order_id = new_order.id
        db.add(oi)
        
    db.commit()
    db.refresh(new_order)
    
    items_response = []
    for oi in new_order.items:
        items_response.append(schemas.OrderItemDetailResponse(
            product_name=oi.product.name,
            qty=oi.qty,
            price_at_order=oi.price_at_order
        ))
        
    return schemas.OrderResponse(
        id=new_order.id,
        customer_name=new_order.customer_name,
        customer_email=new_order.customer_email,
        delivery_address=new_order.delivery_address,
        phone=new_order.phone,
        status=new_order.status,
        created_at=new_order.created_at,
        total=total,
        items=items_response
    )

@router.get("", response_model=List[schemas.OrderResponse])
def get_orders(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(models.Order).filter(models.Order.user_id == current_user.id)
    orders = query.all()
    
    response = []
    for order in orders:
        total = sum([item.qty * item.price_at_order for item in order.items])
        items_response = [
            schemas.OrderItemDetailResponse(
                product_name=item.product.name,
                qty=item.qty,
                price_at_order=item.price_at_order
            ) for item in order.items
        ]
        response.append(schemas.OrderResponse(
            id=order.id,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            delivery_address=order.delivery_address,
            phone=order.phone,
            status=order.status,
            created_at=order.created_at,
            total=total,
            items=items_response
        ))
        
    return response

@router.patch("/{order_id}", response_model=schemas.OrderResponse)
def update_order_status(order_id: int, status_update: schemas.OrderStatusUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order.status = status_update.status
    db.commit()
    db.refresh(order)
    
    total = sum([item.qty * item.price_at_order for item in order.items])
    items_response = [
        schemas.OrderItemDetailResponse(
            product_name=item.product.name,
            qty=item.qty,
            price_at_order=item.price_at_order
        ) for item in order.items
    ]
    
    return schemas.OrderResponse(
        id=order.id,
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        delivery_address=order.delivery_address,
        phone=order.phone,
        status=order.status,
        created_at=order.created_at,
        total=total,
        items=items_response
    )
