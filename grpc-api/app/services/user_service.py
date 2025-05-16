import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf import empty_pb2
from sqlalchemy.ext.asyncio import AsyncSession
from common.database.crud import user_crud
from app.protos import service_pb2, service_pb2_grpc
import traceback

class UserServicer(service_pb2_grpc.UserServiceServicer):
    """Реализация сервиса пользователей"""
    
    def __init__(self, db_factory):
        self.db_factory = db_factory
    
    async def GetUsers(self, request, context):
        """Получить всех пользователей"""
        async for db in self.db_factory():
            users = await user_crud.get_all(db)
            
            # Конвертируем в protobuf
            response = service_pb2.Users()
            for user in users:
                user_pb = response.users.add()
                user_pb.id = user.id
                user_pb.name = user.name
                user_pb.email = user.email
                
                # Конвертируем timestamp
                if user.created_at:
                    created_at = Timestamp()
                    created_at.FromDatetime(user.created_at)
                    user_pb.created_at.CopyFrom(created_at)
                    
            return response
    
    async def GetUser(self, request, context):
        """Получить пользователя по ID"""
        async for db in self.db_factory():
            user = await user_crud.get_by_id(db, request.id)
            
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Пользователь с ID {request.id} не найден")
                return service_pb2.User()
            
            # Конвертируем в protobuf
            response = service_pb2.User()
            response.id = user.id
            response.name = user.name
            response.email = user.email
            
            # Конвертируем timestamp
            if user.created_at:
                created_at = Timestamp()
                created_at.FromDatetime(user.created_at)
                response.created_at.CopyFrom(created_at)
                
            return response
    
    async def CreateUser(self, request, context):
        """Создать нового пользователя"""
        async for db in self.db_factory():
            # Создаем пользователя
            try:
                user = await user_crud.create(db, name=request.name, email=request.email)
            
                # Конвертируем в protobuf
                response = service_pb2.User()
                response.id = user.id
                response.name = user.name
                response.email = user.email
                
                # Конвертируем timestamp
                if user.created_at:
                    created_at = Timestamp()
                    created_at.FromDatetime(user.created_at)
                    response.created_at.CopyFrom(created_at)
                    
                return response
            except Exception as e:
                print("❌ Ошибка при создании пользователя:", str(e))
                traceback.print_exc()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при создании пользователя: {str(e)}")
                return service_pb2.User()
    
    async def DeleteUser(self, request, context):
        """Удалить пользователя"""
        async for db in self.db_factory():
            success = await user_crud.delete(db, request.id)
            
            response = service_pb2.DeleteResponse()
            response.success = success
            
            if success:
                response.message = f"Пользователь с ID {request.id} успешно удален"
            else:
                response.message = f"Пользователь с ID {request.id} не найден"
                context.set_code(grpc.StatusCode.NOT_FOUND)
            
            return response