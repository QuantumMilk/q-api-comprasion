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

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Определение порта для прослушивания
PORT = os.getenv("PORT", "50052")

async def serve():
    """Запуск gRPC сервера с SSL"""
    # Создаем таблицы в базе данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("База данных инициализирована")
    
    # Получаем пути к сертификатам
    ssl_cert_path = os.getenv("SSL_CERT_PATH", "/app/certs/grpc-api.pem")
    
    # Проверяем существование сертификата
    if not os.path.exists(ssl_cert_path):
        logger.error(f"Сертификат не найден по пути: {ssl_cert_path}")
        return
    
    # Читаем содержимое сертификата для получения ключа и сертификата
    with open(ssl_cert_path, 'rb') as f:
        certificate_chain = f.read()
    
    # Создаем учетные данные сервера с SSL
    server_credentials = grpc.ssl_server_credentials(
        [(certificate_chain, certificate_chain)],  # используем один и тот же файл для ключа и сертификата
        root_certificates=None,
        require_client_auth=False  # не требуем клиентской аутентификации
    )
    
    # Создаем gRPC сервер
    server_instance = server()
    
    # Добавляем сервисы
    service_pb2_grpc.add_UserServiceServicer_to_server(UserServicer(get_db), server_instance)
    service_pb2_grpc.add_OrderServiceServicer_to_server(OrderServicer(get_db), server_instance)
    
    service_names = (
        service_pb2.DESCRIPTOR.services_by_name['UserService'].full_name,
        service_pb2.DESCRIPTOR.services_by_name['OrderService'].full_name,
    )
    reflection.enable_server_reflection(service_names, server_instance)

    # Определяем адрес для прослушивания
    listen_addr = f'[::]:{PORT}'
    
    # Добавляем SSL-порт
    server_instance.add_secure_port(listen_addr, server_credentials)
    
    # Запускаем сервер
    await server_instance.start()
    logger.info(f"SSL сервер запущен на {listen_addr}")
    
    try:
        # Держим сервер запущенным
        await server_instance.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания, завершаем работу...")
        await server_instance.stop(0)

if __name__ == '__main__':
    # Запускаем сервер в цикле событий asyncio
    asyncio.run(serve())