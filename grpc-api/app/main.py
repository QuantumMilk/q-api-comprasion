import os
import asyncio
import logging
import grpc
from grpc.aio import server
from grpc_reflection.v1alpha import reflection
from common.database.connection import get_db, engine
from common.models.base import Base
from app.services.user_service import UserServicer
from app.services.order_service import OrderServicer
from app.protos import service_pb2_grpc, service_pb2
from logging.handlers import RotatingFileHandler

# Создание директории для логов, если она не существует
os.makedirs('/app/logs', exist_ok=True)

# Настройка логирования
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Вывод в консоль
        RotatingFileHandler(
            '/app/logs/app.log',
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5                # 5 резервных копий
        )
    ]
)
logger = logging.getLogger(__name__)

# Определение порта для прослушивания
PORT = os.getenv("PORT", "50051")

async def serve():
    """Запуск gRPC сервера"""
    # Создаем таблицы в базе данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized")
    
    # Создаем gRPC сервер
    server_instance = server()
    
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

if __name__ == '__main__':
    # Запускаем сервер в цикле событий asyncio
    asyncio.run(serve())