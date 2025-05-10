import grpc
from google.protobuf import empty_pb2
from sqlalchemy.ext.asyncio import AsyncSession
from common.services import user_service
from common.services.exceptions import NotFoundError, ValidationError, AlreadyExistsError
from common.utils.grpc_mapper import user_to_proto  # Используем gRPC-специфичный маппер
from app.protos import service_pb2, service_pb2_grpc

class UserServicer(service_pb2_grpc.UserServiceServicer):
    """Implementation of the User Service"""
    
    def __init__(self, db_factory):
        self.db_factory = db_factory
    
    async def GetUsers(self, request, context):
        """Get all users"""
        async for db in self.db_factory():
            users = await user_service.get_all(db)
            
            # Convert to protobuf
            response = service_pb2.Users()
            for user in users:
                user_pb = response.users.add()
                # Use the mapper utility
                proto_user = user_to_proto(user)
                user_pb.CopyFrom(proto_user)
                    
            return response
    
    async def GetUser(self, request, context):
        """Get user by ID"""
        async for db in self.db_factory():
            try:
                user = await user_service.get_by_id(db, request.id)
                # Use the mapper utility
                return user_to_proto(user)
            except NotFoundError:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.id} not found")
                return service_pb2.User()
    
    async def CreateUser(self, request, context):
        """Create a new user"""
        async for db in self.db_factory():
            try:
                user = await user_service.create(db, name=request.name, email=request.email)
                # Use the mapper utility
                return user_to_proto(user)
            except ValidationError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return service_pb2.User()
            except AlreadyExistsError as e:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(str(e))
                return service_pb2.User()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Error creating user: {str(e)}")
                return service_pb2.User()
    
    async def DeleteUser(self, request, context):
        """Delete user by ID"""
        async for db in self.db_factory():
            try:
                await user_service.delete(db, request.id)
                
                response = service_pb2.DeleteResponse()
                response.success = True
                response.message = f"User with ID {request.id} successfully deleted"
                
                return response
            except NotFoundError:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                
                response = service_pb2.DeleteResponse()
                response.success = False
                response.message = f"User with ID {request.id} not found"
                
                return response