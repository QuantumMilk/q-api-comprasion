from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Базовая схема пользователя
class UserBase(BaseModel):
    name: str
    email: EmailStr

# Схема для создания пользователя
class UserCreate(UserBase):
    pass

# Схема для обновления пользователя
class UserUpdate(UserBase):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

# Схема для отображения пользователя
class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True