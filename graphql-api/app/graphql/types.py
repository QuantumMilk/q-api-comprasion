# graphql-api/app/graphql/types.py
import strawberry
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from common.models import User as UserModel, Order as OrderModel

@strawberry.type
class User:
    id: int
    name: str
    email: str
    created_at: datetime
    
    @classmethod
    def from_db_model(cls, user: UserModel) -> "User":
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at
        )

@strawberry.type
class Order:
    id: int
    user_id: int
    product_name: str
    price: Decimal
    created_at: datetime
    
    @classmethod
    def from_db_model(cls, order: OrderModel) -> "Order":
        return cls(
            id=order.id,
            user_id=order.user_id,
            product_name=order.product_name,
            price=order.price,
            created_at=order.created_at
        )
        
@strawberry.input
class UserInput:
    name: str = strawberry.field(description="User's full name, cannot be empty")
    email: str = strawberry.field(description="User's email address in valid format (e.g., user@example.com)")
    
@strawberry.input
class OrderInput:
    user_id: int = strawberry.field(description="ID of an existing user")
    product_name: str = strawberry.field(description="Name of the product, cannot be empty")
    price: Decimal = strawberry.field(description="Price with max 2 decimal places, must be greater than zero")

@strawberry.type
class DeletionResult:
    success: bool = strawberry.field(description="Whether the deletion was successful")
    message: str = strawberry.field(description="Detailed message about the deletion operation")