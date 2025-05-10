from typing import Optional
from datetime import datetime
from decimal import Decimal
from common.models.models import User, Order
from google.protobuf.timestamp_pb2 import Timestamp

# Импортируем только в контексте gRPC API
try:
    from app.protos import service_pb2
except ImportError:
    # Если мы не в gRPC контексте, создаем заглушку
    service_pb2 = None

def datetime_to_timestamp(dt: Optional[datetime]) -> Optional[Timestamp]:
    """Convert Python datetime to Protobuf Timestamp"""
    if not dt or service_pb2 is None:
        return None
    
    timestamp = Timestamp()
    timestamp.FromDatetime(dt)
    return timestamp

def user_to_proto(user: User):
    """Convert User model to protobuf User message"""
    if not user or service_pb2 is None:
        return None
    
    user_proto = service_pb2.User()
    user_proto.id = user.id
    user_proto.name = user.name
    user_proto.email = user.email
    
    if user.created_at:
        created_ts = datetime_to_timestamp(user.created_at)
        if created_ts:
            user_proto.created_at.CopyFrom(created_ts)
    
    return user_proto

def order_to_proto(order: Order):
    """Convert Order model to protobuf Order message"""
    if not order or service_pb2 is None:
        return None
    
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
        created_ts = datetime_to_timestamp(order.created_at)
        if created_ts:
            order_proto.created_at.CopyFrom(created_ts)
    
    return order_proto