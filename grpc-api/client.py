import grpc
import asyncio
from app.protos import service_pb2, service_pb2_grpc
from google.protobuf import empty_pb2

async def test_user_service():
    """Тестирование сервиса пользователей"""
    # Устанавливаем соединение с сервером
    channel = grpc.aio.insecure_channel('localhost:50051')
    stub = service_pb2_grpc.UserServiceStub(channel)
    
    print("=== Тестирование сервиса пользователей ===")
    
    # Создание пользователя
    print("\n-> Создание пользователя:")
    user = await stub.CreateUser(service_pb2.CreateUserRequest(
        name="Иван Иванов",
        email="ivan@example.com"
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

async def test_order_service():
    """Тестирование сервиса заказов"""
    # Устанавливаем соединение с сервером
    channel = grpc.aio.insecure_channel('localhost:50051')
    user_stub = service_pb2_grpc.UserServiceStub(channel)
    order_stub = service_pb2_grpc.OrderServiceStub(channel)
    
    print("\n=== Тестирование сервиса заказов ===")
    
    # Создаем пользователя для заказов
    user = await user_stub.CreateUser(service_pb2.CreateUserRequest(
        name="Петр Петров",
        email="petr@example.com"
    ))
    print(f"\nСоздан пользователь для заказов: id={user.id}, name={user.name}")
    
    # Создание заказа
    print("\n-> Создание заказа:")
    order = await order_stub.CreateOrder(service_pb2.CreateOrderRequest(
        user_id=user.id,
        product_name="Ноутбук",
        price=1299.99
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

async def main():
    # Запускаем тесты
    await test_user_service()
    await test_order_service()

if __name__ == '__main__':
    # Запускаем тесты в цикле событий asyncio
    asyncio.run(main())