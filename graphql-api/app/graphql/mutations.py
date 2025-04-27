import strawberry
from typing import Optional
from .types import User, Order, UserInput, OrderInput
from common.database.connection import async_session  # Заменяем AsyncSessionLocal на async_session
from common.database.crud import user_crud, order_crud
from decimal import Decimal

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, input: UserInput) -> User:
        async with async_session() as db:  # Используем async_session вместо AsyncSessionLocal
            user = await user_crud.create(db, name=input.name, email=input.email)
            return User.from_db_model(user)
    
    @strawberry.mutation
    async def delete_user(self, id: int) -> bool:
        async with async_session() as db:  # Используем async_session вместо AsyncSessionLocal
            return await user_crud.delete(db, id)
    
    @strawberry.mutation
    async def create_order(self, input: OrderInput) -> Order:
        async with async_session() as db:  # Используем async_session вместо AsyncSessionLocal
            order = await order_crud.create(
                db, 
                user_id=input.user_id, 
                product_name=input.product_name, 
                price=input.price
            )
            return Order.from_db_model(order)
    
    @strawberry.mutation
    async def delete_order(self, id: int) -> bool:
        async with async_session() as db:  # Используем async_session вместо AsyncSessionLocal
            return await order_crud.delete(db, id)