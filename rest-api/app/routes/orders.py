from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from common.database.connection import get_db
from common.services import order_service  # Используем сервис вместо CRUD
from common.services.exceptions import NotFoundError, ValidationError
from app.schemas import OrderCreate, OrderUpdate, OrderResponse
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/", response_model=List[OrderResponse])
async def get_orders(db: AsyncSession = Depends(get_db)):
    """Get all orders"""
    return await order_service.get_all(db)

@router.get("/user/{user_id}", response_model=List[OrderResponse])
async def get_user_orders(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get orders by user ID"""
    try:
        return await order_service.get_by_user_id(db, user_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    """Get order by ID"""
    try:
        return await order_service.get_by_id(db, order_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Order not found")

@router.post("/", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    """Create a new order"""
    try:
        return await order_service.create(
            db, 
            user_id=order.user_id, 
            product_name=order.product_name, 
            price=order.price
        )
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{order_id}")
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db)):
    """Delete order by ID"""
    try:
        await order_service.delete(db, order_id)
        return {"success": True, "message": "Order deleted successfully"}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Order not found")