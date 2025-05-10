import strawberry
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from common.models import User as UserModel, Order as OrderModel
from common.utils.mapper import model_to_dict

@strawberry.type
class User:
    id: int
    name: str
    email: str
    created_at: datetime
    
    @classmethod
    def from_db_model(cls, user: UserModel) -> "User":
        """Convert ORM model to GraphQL type using mapper"""
        if not user:
            return None
        
        user_dict = model_to_dict(user)
        return cls(
            id=user_dict['id'],
            name=user_dict['name'],
            email=user_dict['email'],
            created_at=user_dict['created_at']
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
        """Convert ORM model to GraphQL type using mapper"""
        if not order:
            return None
        
        order_dict = model_to_dict(order)
        return cls(
            id=order_dict['id'],
            user_id=order_dict['user_id'],
            product_name=order_dict['product_name'],
            price=order_dict['price'],
            created_at=order_dict['created_at']
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