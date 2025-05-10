import strawberry
from typing import Optional
from .types import User, Order, UserInput, OrderInput, DeletionResult
from common.database.connection import async_session
from common.services import user_service, order_service  # Используем сервисы вместо CRUD
from common.services.exceptions import NotFoundError, ValidationError, AlreadyExistsError
from strawberry.types import Info
from decimal import Decimal

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, input: UserInput) -> User:
        async with async_session() as db:
            try:
                user = await user_service.create(db, name=input.name, email=input.email)
                return User.from_db_model(user)
            except ValidationError as e:
                raise ValueError(str(e))
            except AlreadyExistsError as e:
                raise ValueError(str(e))
    
    @strawberry.mutation
    async def delete_user(self, id: int) -> DeletionResult:
        async with async_session() as db:
            try:
                await user_service.delete(db, id)
                return DeletionResult(success=True, message="User deleted successfully")
            except NotFoundError:
                return DeletionResult(success=False, message=f"User with ID {id} not found")
    
    @strawberry.mutation
    async def create_order(self, input: OrderInput) -> Order:
        async with async_session() as db:
            try:
                order = await order_service.create(
                    db, 
                    user_id=input.user_id, 
                    product_name=input.product_name, 
                    price=input.price
                )
                return Order.from_db_model(order)
            except NotFoundError:
                raise ValueError(f"User with ID {input.user_id} not found")
            except ValidationError as e:
                raise ValueError(str(e))
    
    @strawberry.mutation
    async def delete_order(self, id: int) -> DeletionResult:
        async with async_session() as db:
            try:
                await order_service.delete(db, id)
                return DeletionResult(success=True, message="Order deleted successfully")
            except NotFoundError:
                return DeletionResult(success=False, message=f"Order with ID {id} not found")