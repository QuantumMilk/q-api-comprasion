import grpc
from google.protobuf import empty_pb2
from sqlalchemy.ext.asyncio import AsyncSession
from common.services import order_service
from common.services.exceptions import NotFoundError, ValidationError
from common.utils.mapper import order_to_proto, datetime_to_timestamp
from app.protos import service_pb2, service_pb2_grpc
from decimal import Decimal

class OrderServicer(service_pb2_grpc.OrderServiceServicer):
    """Implementation of the Order Service"""
    
    def __init__(self, db_factory):
        self.db_factory = db_factory
    
    async def GetOrders(self, request, context):
        """Get all orders"""
        async for db in self.db_factory():
            orders = await order_service.get_all(db)
            
            # Convert to protobuf
            response = service_pb2.Orders()
            for order in orders:
                order_pb = response.orders.add()
                # Use the mapper utility
                proto_order = order_to_proto(order)
                order_pb.CopyFrom(proto_order)
                    
            return response
    
    async def GetOrdersByUser(self, request, context):
        """Get orders for a specific user"""
        async for db in self.db_factory():
            try:
                orders = await order_service.get_by_user_id(db, request.id)
                
                # Convert to protobuf
                response = service_pb2.Orders()
                for order in orders:
                    order_pb = response.orders.add()
                    # Use the mapper utility
                    proto_order = order_to_proto(order)
                    order_pb.CopyFrom(proto_order)
                        
                return response
            except NotFoundError:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.id} not found")
                return service_pb2.Orders()
    
    async def CreateOrder(self, request, context):
        """Create a new order"""
        async for db in self.db_factory():
            try:
                order = await order_service.create(
                    db, 
                    user_id=request.user_id, 
                    product_name=request.product_name, 
                    price=Decimal(str(request.price))
                )
                
                # Use the mapper utility
                return order_to_proto(order)
            except NotFoundError:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.user_id} not found")
                return service_pb2.Order()
            except ValidationError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return service_pb2.Order()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Error creating order: {str(e)}")
                return service_pb2.Order()
    
    async def DeleteOrder(self, request, context):
        """Delete order by ID"""
        async for db in self.db_factory():
            try:
                await order_service.delete(db, request.id)
                
                response = service_pb2.DeleteResponse()
                response.success = True
                response.message = f"Order with ID {request.id} successfully deleted"
                
                return response
            except NotFoundError:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                
                response = service_pb2.DeleteResponse()
                response.success = False
                response.message = f"Order with ID {request.id} not found"
                
                return response