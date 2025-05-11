import os
import asyncio
import grpc
from grpc.aio import server
from grpc_reflection.v1alpha import reflection
from common.database.connection import get_db, engine
from common.models.base import Base
from app.services.user_service import UserServicer
from app.services.order_service import OrderServicer
from app.logging_interceptor import LoggingInterceptor
from app.protos import service_pb2_grpc, service_pb2
from common.utils.logging import get_logger

# Настройка логирования
logger = get_logger("grpc_api", "grpc_api.log")

# Определение порта для прослушивания
PORT = os.getenv("PORT", "50051")

async def serve():
    """Запуск gRPC сервера"""
    # Создаем таблицы в базе данных
    logger.info("Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")
    
    # Создаем gRPC сервер с интерцептором для логирования
    server_instance = server(interceptors=[LoggingInterceptor()])
    
    # Добавляем сервисы
    service_pb2_grpc.add_UserServiceServicer_to_server(UserServicer(get_db), server_instance)
    service_pb2_grpc.add_OrderServiceServicer_to_server(OrderServicer(get_db), server_instance)
    
    service_names = (
        service_pb2.DESCRIPTOR.services_by_name['UserService'].full_name,
        service_pb2.DESCRIPTOR.services_by_name['OrderService'].full_name,
        'grpc.health.v1.Health',  # Добавляем сервис проверки здоровья
    )
    reflection.enable_server_reflection(service_names, server_instance)

    # Определяем адрес для прослушивания
    listen_addr = f'[::]:{PORT}'
    server_instance.add_insecure_port(listen_addr)
    
    # Запускаем сервер
    await server_instance.start()
    logger.info(f"Server started on {listen_addr}")
    
    try:
        # Держим сервер запущенным
        await server_instance.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Received interruption signal, shutting down...")
        await server_instance.stop(0)
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=e)
        await server_instance.stop(0)

if __name__ == '__main__':
    # Запускаем сервер в цикле событий asyncio
    asyncio.run(serve())