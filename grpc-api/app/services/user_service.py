import grpc
from google.protobuf import empty_pb2
from sqlalchemy.ext.asyncio import AsyncSession
from common.services import user_service
from common.services.exceptions import NotFoundError, ValidationError, AlreadyExistsError
from common.utils.grpc_mapper import user_to_proto
from common.utils.logging import get_logger, log_business_event
from app.protos import service_pb2, service_pb2_grpc

logger = get_logger("grpc_user_service", "grpc_user_service.log")

class UserServicer(service_pb2_grpc.UserServiceServicer):
    """Implementation of the User Service"""
    
    def __init__(self, db_factory):
        self.db_factory = db_factory
    
    async def GetUsers(self, request, context):
        """Get all users"""
        logger.info("GetUsers called")
        async for db in self.db_factory():
            users = await user_service.get_all(db)
            
            # Convert to protobuf
            response = service_pb2.Users()
            for user in users:
                user_pb = response.users.add()
                # Use the mapper utility
                proto_user = user_to_proto(user)
                user_pb.CopyFrom(proto_user)
            
            logger.info(f"GetUsers returned {len(response.users)} users")
            return response
    
    async def GetUser(self, request, context):
        """Get user by ID"""
        user_id = request.id
        logger.info(f"GetUser called with ID: {user_id}")
        async for db in self.db_factory():
            try:
                user = await user_service.get_by_id(db, user_id)
                # Use the mapper utility
                result = user_to_proto(user)
                logger.info(f"GetUser returned user with ID: {user_id}")
                return result
            except NotFoundError:
                logger.warning(f"User with ID {user_id} not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {user_id} not found")
                return service_pb2.User()
    
    async def CreateUser(self, request, context):
        """Create a new user"""
        name = request.name
        email = request.email
        logger.info(f"CreateUser called with name: {name}, email: {email}")
        async for db in self.db_factory():
            try:
                user = await user_service.create(db, name=name, email=email)
                # Use the mapper utility
                result = user_to_proto(user)
                logger.info(f"CreateUser created user with ID: {user.id}")
                log_business_event(
                    logger, 
                    "created", 
                    "user", 
                    user.id, 
                    {"name": name, "email": email}
                )
                return result
            except ValidationError as e:
                logger.warning(f"Validation error: {str(e)}")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return service_pb2.User()
            except AlreadyExistsError as e:
                logger.warning(f"Already exists error: {str(e)}")
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(str(e))
                return service_pb2.User()
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}", exc_info=e)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Error creating user: {str(e)}")
                return service_pb2.User()
    
    async def DeleteUser(self, request, context):
        """Delete user by ID"""
        user_id = request.id
        logger.info(f"DeleteUser called with ID: {user_id}")
        async for db in self.db_factory():
            try:
                await user_service.delete(db, user_id)
                
                response = service_pb2.DeleteResponse()
                response.success = True
                response.message = f"User with ID {user_id} successfully deleted"
                
                logger.info(f"DeleteUser successfully deleted user with ID: {user_id}")
                log_business_event(logger, "deleted", "user", user_id)
                return response
            except NotFoundError:
                logger.warning(f"Cannot delete: User with ID {user_id} not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                
                response = service_pb2.DeleteResponse()
                response.success = False
                response.message = f"User with ID {user_id} not found"
                
                return response