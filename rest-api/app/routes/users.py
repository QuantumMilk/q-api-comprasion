from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from common.database.connection import get_db
from common.database.crud import user_crud
from app.schemas import UserCreate, UserUpdate, UserResponse
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db)):
    """Получение всех пользователей"""
    users = await user_crud.get_all(db)
    return [user for user in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Получение пользователя по ID"""
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Создание нового пользователя"""
    return await user_crud.create(db, name=user.name, email=user.email)

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Удаление пользователя"""
    success = await user_crud.delete(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}