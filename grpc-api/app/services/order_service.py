import grpc
from google.protobuf import empty_pb2
from sqlalchemy.ext.asyncio import AsyncSession
from common.services import order_service
from common.services.exceptions import NotFoundError, ValidationError
from common.utils.grpc_mapper import order_to_proto
from common.utils.logging import get_logger, log_business_event
from app.protos import service_pb2, service_pb2_grpc
from decimal import Decimal

logger = get_logger("grpc_order_service", "grpc_order_service.log")

class OrderServicer(service_pb2_grpc.OrderServiceServicer):
    """Implementation of the Order Service"""
    
    def __init__(self, db_factory):
        self.db_factory = db_factory
    
    async def GetOrders(self, request, context):
        """Get all orders"""
        logger.info("GetOrders called")
        async for db in self.db_factory():
            orders = await order_service.get_all(db)
            
            # Convert to protobuf
            response = service_pb2.Orders()
            for order in orders:
                order_pb = response.orders.add()
                # Use the mapper utility
                proto_order = order_to_proto(order)
                order_pb.CopyFrom(proto_order)
            
            logger.info(f"GetOrders returned {len(response.orders)} orders")
            return response
    
    async def GetOrdersByUser(self, request, context):
        """Get orders for a specific user"""
        user_id = request.id
        logger.info(f"GetOrdersByUser called with user ID: {user_id}")
        async for db in self.db_factory():
            try:
                orders = await order_service.get_by_user_id(db, user_id)
                
                # Convert to protobuf
                response = service_pb2.Orders()
                for order in orders:
                    order_pb = response.orders.add()
                    # Use the mapper utility
                    proto_order = order_to_proto(order)
                    order_pb.CopyFrom(proto_order)
                
                logger.info(f"GetOrdersByUser returned {len(response.orders)} orders for user ID: {user_id}")
                return response
            except NotFoundError:
                logger.warning(f"User with ID {user_id} not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {user_id} not found")
                return service_pb2.Orders()
    
    async def CreateOrder(self, request, context):
        """Create a new order"""
        user_id = request.user_id
        product_name = request.product_name
        price = request.price
        logger.info(f"CreateOrder called with user_id: {user_id}, product_name: {product_name}, price: {price}")
        async for db in self.db_factory():
            try:
                order = await order_service.create(
                    db, 
                    user_id=user_id, 
                    product_name=product_name, 
                    price=Decimal(str(price))
                )
                
                # Use the mapper utility
                result = order_to_proto(order)
                logger.info(f"CreateOrder created order with ID: {order.id}")
                log_business_event(
                    logger, 
                    "created", 
                    "order", 
                    order.id, 
                    {"user_id": user_id, "product_name": product_name, "price": str(price)}
                )
                return result
            except NotFoundError:
                logger.warning(f"User with ID {user_id} not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {user_id} not found")
                return service_pb2.Order()
            except ValidationError as e:
                logger.warning(f"Validation error: {str(e)}")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return service_pb2.Order()
            except Exception as e:
                logger.error(f"Error creating order: {str(e)}", exc_info=e)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Error creating order: {str(e)}")
                return service_pb2.Order()
    
    async def DeleteOrder(self, request, context):
        """Delete order by ID"""
        order_id = request.id
        logger.info(f"DeleteOrder called with ID: {order_id}")
        async for db in self.db_factory():
            try:
                # Получаем заказ перед удалением для логирования
                order = await order_service.get_by_id(db, order_id)
                user_id = order.user_id
                product_name = order.product_name
                
                await order_service.delete(db, order_id)
                
                response = service_pb2.DeleteResponse()
                response.success = True
                response.message = f"Order with ID {order_id} successfully deleted"
                
                logger.info(f"DeleteOrder successfully deleted order with ID: {order_id}")
                log_business_event(
                    logger, 
                    "deleted", 
                    "order", 
                    order_id, 
                    {"user_id": user_id, "product_name": product_name}
                )
                return response
            except NotFoundError:
                logger.warning(f"Cannot delete: Order with ID {order_id} not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                
                response = service_pb2.DeleteResponse()
                response.success = False
                response.message = f"Order with ID {order_id} not found"
                
                return response