from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from common.database.connection import get_db
from common.services import user_service  
from common.services.exceptions import NotFoundError, ValidationError, AlreadyExistsError
from app.schemas import UserCreate, UserUpdate, UserResponse, DeleteResponse
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db)):
    """Get all users"""
    return await user_service.get_all(db)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user by ID"""
    try:
        return await user_service.get_by_id(db, user_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user"""
    try:
        return await user_service.create(db, name=user.name, email=user.email)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}", response_model=DeleteResponse)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Delete user by ID"""
    try:
        await user_service.delete(db, user_id)
        return DeleteResponse(success=True, message=f"User deleted successfully")
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")