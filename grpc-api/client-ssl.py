import grpc
import asyncio
import os
import ssl
from app.protos import service_pb2, service_pb2_grpc
from google.protobuf import empty_pb2

async def test_user_service_ssl():
    """Тестирование сервиса пользователей через SSL"""
    
    # Получаем сертификат CA
    ca_cert_path = os.getenv("CA_CERT_PATH", "/app/certs/ca.crt")
    
    # Читаем CA сертификат
    with open(ca_cert_path, 'rb') as f:
        ca_cert = f.read()
    
    # Создаем учетные данные для SSL
    credentials = grpc.ssl_channel_credentials(root_certificates=ca_cert)
    
    # Устанавливаем защищенное соединение с сервером
    channel = grpc.aio.secure_channel('grpc-api-ssl:50052', credentials)
    stub = service_pb2_grpc.UserServiceStub(channel)
    
    print("=== Тестирование сервиса пользователей через SSL ===")
    
    try:
        # Создание пользователя
        print("\n-> Создание пользователя:")
        user = await stub.CreateUser(service_pb2.CreateUserRequest(
            name="Иван Иванов (SSL)",
            email="ivan_ssl@example.com"
        ))
        print(f"Создан пользователь: id={user.id}, name={user.name}, email={user.email}")
        
        # Получение пользователя
        print("\n-> Получение пользователя:")
        user = await stub.GetUser(service_pb2.UserRequest(id=user.id))
        print(f"Получен пользователь: id={user.id}, name={user.name}, email={user.email}")
        
        # Получение всех пользователей
        print("\n-> Получение всех пользователей:")
        users = await stub.GetUsers(empty_pb2.Empty())
        for u in users.users:
            print(f"Пользователь: id={u.id}, name={u.name}, email={u.email}")
        
        # Удаление пользователя
        print("\n-> Удаление пользователя:")
        response = await stub.DeleteUser(service_pb2.UserRequest(id=user.id))
        print(f"Результат удаления: {response.success}, сообщение: {response.message}")
    
    except grpc.RpcError as e:
        print(f"Ошибка RPC: {e.code()}, {e.details()}")
    
    await channel.close()

async def test_order_service_ssl():
    """Тестирование сервиса заказов через SSL"""
    
    # Получаем сертификат CA
    ca_cert_path = os.getenv("CA_CERT_PATH", "/app/certs/ca.crt")
    
    # Читаем CA сертификат
    with open(ca_cert_path, 'rb') as f:
        ca_cert = f.read()
    
    # Создаем учетные данные для SSL
    credentials = grpc.ssl_channel_credentials(root_certificates=ca_cert)
    
    # Устанавливаем защищенное соединение с сервером
    channel = grpc.aio.secure_channel('grpc-api-ssl:50052', credentials)
    user_stub = service_pb2_grpc.UserServiceStub(channel)
    order_stub = service_pb2_grpc.OrderServiceStub(channel)
    
    print("\n=== Тестирование сервиса заказов через SSL ===")
    
    try:
        # Создаем пользователя для заказов
        user = await user_stub.CreateUser(service_pb2.CreateUserRequest(
            name="Петр Петров (SSL)",
            email="petr_ssl@example.com"
        ))
        print(f"\nСоздан пользователь для заказов: id={user.id}, name={user.name}")
        
        # Создание заказа
        print("\n-> Создание заказа:")
        order = await order_stub.CreateOrder(service_pb2.CreateOrderRequest(
            user_id=user.id,
            product_name="Ноутбук (SSL)",
            price=1399.99
        ))
        print(f"Создан заказ: id={order.id}, user_id={order.user_id}, product={order.product_name}, price={order.price}")
        
        # Получение заказов пользователя
        print("\n-> Получение заказов пользователя:")
        orders = await order_stub.GetOrdersByUser(service_pb2.UserRequest(id=user.id))
        for o in orders.orders:
            print(f"Заказ: id={o.id}, user_id={o.user_id}, product={o.product_name}, price={o.price}")
        
        # Получение всех заказов
        print("\n-> Получение всех заказов:")
        all_orders = await order_stub.GetOrders(empty_pb2.Empty())
        for o in all_orders.orders:
            print(f"Заказ: id={o.id}, user_id={o.user_id}, product={o.product_name}, price={o.price}")
        
        # Удаление заказа
        print("\n-> Удаление заказа:")
        response = await order_stub.DeleteOrder(service_pb2.OrderRequest(id=order.id))
        print(f"Результат удаления заказа: {response.success}, сообщение: {response.message}")
        
        # Удаляем тестового пользователя
        await user_stub.DeleteUser(service_pb2.UserRequest(id=user.id))
    
    except grpc.RpcError as e:
        print(f"Ошибка RPC: {e.code()}, {e.details()}")
    
    await channel.close()

async def main():
    # Запускаем тесты
    await test_user_service_ssl()
    await test_order_service_ssl()

if __name__ == '__main__':
    # Запускаем тесты в цикле событий asyncio
    asyncio.run(main())