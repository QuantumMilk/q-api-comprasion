import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf import empty_pb2
from sqlalchemy.ext.asyncio import AsyncSession
from common.database.crud import order_crud, user_crud
from app.protos import service_pb2, service_pb2_grpc
from decimal import Decimal

class OrderServicer(service_pb2_grpc.OrderServiceServicer):
    """Реализация сервиса заказов"""
    
    def __init__(self, db_factory):
        self.db_factory = db_factory
    
    async def GetOrders(self, request, context):
        """Получить все заказы"""
        async for db in self.db_factory():
            orders = await order_crud.get_all(db)
            
            # Конвертируем в protobuf
            response = service_pb2.Orders()
            for order in orders:
                order_pb = response.orders.add()
                order_pb.id = order.id
                order_pb.user_id = order.user_id
                order_pb.product_name = order.product_name
                order_pb.price = float(order.price)
                
                # Конвертируем timestamp
                if order.created_at:
                    created_at = Timestamp()
                    created_at.FromDatetime(order.created_at)
                    order_pb.created_at.CopyFrom(created_at)
                    
            return response
    
    async def GetOrdersByUser(self, request, context):
        """Получить заказы пользователя"""
        async for db in self.db_factory():
            # Проверяем существование пользователя
            user = await user_crud.get_by_id(db, request.id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Пользователь с ID {request.id} не найден")
                return service_pb2.Orders()
                
            orders = await order_crud.get_by_user_id(db, request.id)
            
            # Конвертируем в protobuf
            response = service_pb2.Orders()
            for order in orders:
                order_pb = response.orders.add()
                order_pb.id = order.id
                order_pb.user_id = order.user_id
                order_pb.product_name = order.product_name
                order_pb.price = float(order.price)
                
                # Конвертируем timestamp
                if order.created_at:
                    created_at = Timestamp()
                    created_at.FromDatetime(order.created_at)
                    order_pb.created_at.CopyFrom(created_at)
                    
            return response
    
    async def CreateOrder(self, request, context):
        """Создать новый заказ"""
        async for db in self.db_factory():
            # Проверяем существование пользователя
            user = await user_crud.get_by_id(db, request.user_id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Пользователь с ID {request.user_id} не найден")
                return service_pb2.Order()
                
            try:
                # Создаем заказ
                order = await order_crud.create(
                    db, 
                    user_id=request.user_id, 
                    product_name=request.product_name, 
                    price=Decimal(str(request.price))
                )
                
                # Конвертируем в protobuf
                response = service_pb2.Order()
                response.id = order.id
                response.user_id = order.user_id
                response.product_name = order.product_name
                response.price = float(order.price)
                
                # Конвертируем timestamp
                if order.created_at:
                    created_at = Timestamp()
                    created_at.FromDatetime(order.created_at)
                    response.created_at.CopyFrom(created_at)
                    
                return response
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при создании заказа: {str(e)}")
                return service_pb2.Order()
    
    async def DeleteOrder(self, request, context):
        """Удалить заказ"""
        async for db in self.db_factory():
            success = await order_crud.delete(db, request.id)
            
            response = service_pb2.DeleteResponse()
            response.success = success
            
            if success:
                response.message = f"Заказ с ID {request.id} успешно удален"
            else:
                response.message = f"Заказ с ID {request.id} не найден"
                context.set_code(grpc.StatusCode.NOT_FOUND)
            
            return response