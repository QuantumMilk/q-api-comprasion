import strawberry
from typing import List, Optional
from .types import User, Order
from common.database.connection import get_db, async_session  # Заменяем AsyncSessionLocal на async_session
from common.database.crud import user_crud, order_crud
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info

@strawberry.type
class Query:
    @strawberry.field
    async def users(self) -> List[User]:
        async with async_session() as db:  # Используем async_session вместо AsyncSessionLocal
            users = await user_crud.get_all(db)
            return [User.from_db_model(user) for user in users]
    
    @strawberry.field
    async def user(self, id: int) -> Optional[User]:
        async with async_session() as db:  # Используем async_session вместо AsyncSessionLocal
            user = await user_crud.get_by_id(db, id)
            if user:
                return User.from_db_model(user)
            return None
    
    @strawberry.field
    async def orders(self) -> List[Order]:
        async with async_session() as db:  # Используем async_session вместо AsyncSessionLocal
            orders = await order_crud.get_all(db)
            return [Order.from_db_model(order) for order in orders]
    
    @strawberry.field
    async def orders_by_user(self, user_id: int) -> List[Order]:
        async with async_session() as db:  # Используем async_session вместо AsyncSessionLocal
            orders = await order_crud.get_by_user_id(db, user_id)
            return [Order.from_db_model(order) for order in orders]