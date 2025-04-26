from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from common.database.connection import get_db
from common.database.crud import order_crud, user_crud
from app.schemas import OrderCreate, OrderUpdate, OrderResponse
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/", response_model=List[OrderResponse])
async def get_orders(db: AsyncSession = Depends(get_db)):
    """Получение всех заказов"""
    return await order_crud.get_all(db)

@router.get("/user/{user_id}", response_model=List[OrderResponse])
async def get_user_orders(user_id: int, db: AsyncSession = Depends(get_db)):
    """Получение заказов пользователя"""
    # Проверяем существование пользователя
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return await order_crud.get_by_user_id(db, user_id)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    """Получение заказа по ID"""
    order = await order_crud.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    """Создание нового заказа"""
    # Проверяем существование пользователя
    user = await user_crud.get_by_id(db, order.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return await order_crud.create(
        db, 
        user_id=order.user_id, 
        product_name=order.product_name, 
        price=order.price
    )

@router.delete("/{order_id}")
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db)):
    """Удаление заказа"""
    success = await order_crud.delete(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}