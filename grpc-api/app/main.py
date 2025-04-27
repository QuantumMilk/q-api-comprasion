import os
import asyncio
import logging
import grpc
from grpc.aio import server
from common.database.connection import get_db, engine
from common.models.base import Base
from app.services.user_service import UserServicer
from app.services.order_service import OrderServicer
from app.protos import service_pb2_grpc

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Определение порта для прослушивания
PORT = os.getenv("PORT", "50051")

async def serve():
    """Запуск gRPC сервера"""
    # Создаем таблицы в базе данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("База данных инициализирована")
    
    # Создаем gRPC сервер
    server_instance = server()
    
    # Добавляем сервисы
    service_pb2_grpc.add_UserServiceServicer_to_server(UserServicer(get_db), server_instance)
    service_pb2_grpc.add_OrderServiceServicer_to_server(OrderServicer(get_db), server_instance)
    
    # Определяем адрес для прослушивания
    listen_addr = f'[::]:{PORT}'
    server_instance.add_insecure_port(listen_addr)
    
    # Запускаем сервер
    await server_instance.start()
    logger.info(f"Сервер запущен на {listen_addr}")
    
    try:
        # Держим сервер запущенным
        await server_instance.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания, завершаем работу...")
        await server_instance.stop(0)

if __name__ == '__main__':
    # Запускаем сервер в цикле событий asyncio
    asyncio.run(serve())