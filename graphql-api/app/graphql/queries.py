import strawberry
from typing import List, Optional
from .types import User, Order
from common.database.connection import get_db, async_session
from common.services import user_service, order_service  # Используем сервисы вместо CRUD
from common.services.exceptions import NotFoundError
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info

@strawberry.type
class Query:
    @strawberry.field
    async def users(self) -> List[User]:
        async with async_session() as db:
            users = await user_service.get_all(db)
            return [User.from_db_model(user) for user in users]
    
    @strawberry.field
    async def user(self, id: int) -> Optional[User]:
        async with async_session() as db:
            try:
                user = await user_service.get_by_id(db, id)
                return User.from_db_model(user)
            except NotFoundError:
                return None
    
    @strawberry.field
    async def orders(self) -> List[Order]:
        async with async_session() as db:
            orders = await order_service.get_all(db)
            return [Order.from_db_model(order) for order in orders]
    
    @strawberry.field
    async def orders_by_user(self, user_id: int) -> List[Order]:
        async with async_session() as db:
            try:
                orders = await order_service.get_by_user_id(db, user_id)
                return [Order.from_db_model(order) for order in orders]
            except NotFoundError:
                # GraphQL может вернуть пустой список в случае отсутствия данных
                # но для единообразия лучше добавить error в errors
                raise ValueError(f"User with ID {user_id} not found")