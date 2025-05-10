from typing import Dict, Any, Type, TypeVar, Optional
from datetime import datetime
from decimal import Decimal
from google.protobuf.timestamp_pb2 import Timestamp
from sqlalchemy.orm import DeclarativeBase
from common.models.models import User, Order
from app.protos import service_pb2

T = TypeVar('T', bound=DeclarativeBase)

def model_to_dict(model: T) -> Dict[str, Any]:
    """Convert SQLAlchemy model to dictionary"""
    if model is None:
        return {}
    
    result = {}
    for column in model.__table__.columns:
        value = getattr(model, column.name)
        result[column.name] = value
    
    return result

def datetime_to_timestamp(dt: Optional[datetime]) -> Optional[Timestamp]:
    """Convert Python datetime to Protobuf Timestamp"""
    if not dt:
        return None
    
    timestamp = Timestamp()
    timestamp.FromDatetime(dt)
    return timestamp

def user_to_proto(user: User) -> service_pb2.User:
    """Convert User model to protobuf User message"""
    if not user:
        return service_pb2.User()
    
    user_proto = service_pb2.User()
    user_proto.id = user.id
    user_proto.name = user.name
    user_proto.email = user.email
    
    if user.created_at:
        user_proto.created_at.CopyFrom(datetime_to_timestamp(user.created_at))
    
    return user_proto

def order_to_proto(order: Order) -> service_pb2.Order:
    """Convert Order model to protobuf Order message"""
    if not order:
        return service_pb2.Order()
    
    order_proto = service_pb2.Order()
    order_proto.id = order.id
    order_proto.user_id = order.user_id
    order_proto.product_name = order.product_name
    
    # Handle Decimal to float conversion safely
    if isinstance(order.price, Decimal):
        order_proto.price = float(order.price)
    else:
        order_proto.price = 0.0
    
    if order.created_at:
        order_proto.created_at.CopyFrom(datetime_to_timestamp(order.created_at))
    
    return order_proto