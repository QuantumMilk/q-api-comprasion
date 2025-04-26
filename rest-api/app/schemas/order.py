from pydantic import BaseModel, condecimal
from datetime import datetime
from typing import Optional

# Базовая схема заказа
class OrderBase(BaseModel):
    user_id: int
    product_name: str
    price: condecimal(max_digits=10, decimal_places=2)

# Схема для создания заказа
class OrderCreate(OrderBase):
    pass

# Схема для обновления заказа
class OrderUpdate(BaseModel):
    product_name: Optional[str] = None
    price: Optional[condecimal(max_digits=10, decimal_places=2)] = None

# Схема для отображения заказа
class OrderResponse(OrderBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True