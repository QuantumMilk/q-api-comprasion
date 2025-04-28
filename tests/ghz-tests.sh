#!/bin/bash

# Создаем директорию для результатов, если она не существует
mkdir -p results/grpc

# Определяем путь к proto-файлу
PROTO_PATH="/tests/protos/service.proto"

# Проверяем, существует ли файл
if [ ! -f "$PROTO_PATH" ]; then
  echo "ОШИБКА: Proto-файл не найден по пути $PROTO_PATH"
  exit 1
fi

echo "Используется proto-файл: $PROTO_PATH"

# Тест задержки (Latency test) для gRPC
echo "Запуск теста задержки для gRPC..."

ghz \
  --proto "$PROTO_PATH" \
  --call usersorders.UserService.GetUsers \
  --insecure \
  --total 100 \
  --concurrency 1 \
  ${GRPC_API_URL} \
  --format json > results/grpc/latency_test.json

echo "Тест задержки для gRPC завершен."

# Тест пропускной способности (Throughput test) для gRPC
echo "Запуск теста пропускной способности для gRPC..."

ghz \
  --proto "$PROTO_PATH" \
  --call usersorders.UserService.GetUsers \
  --insecure \
  --total 3000 \
  --concurrency 50 \
  --rps 100 \
  --duration 30s \
  ${GRPC_API_URL} \
  --format json > results/grpc/throughput_test.json

echo "Тест пропускной способности для gRPC завершен."

# Тест поведения под нагрузкой (Load test) для gRPC
echo "Запуск теста поведения под нагрузкой для gRPC..."

# Тест с 1 пользователем
ghz \
  --proto "$PROTO_PATH" \
  --call usersorders.UserService.GetUsers \
  --insecure \
  --concurrency 1 \
  --duration 30s \
  ${GRPC_API_URL} \
  --format json > results/grpc/load_test_1vu.json

# Тест с 10 пользователями
ghz \
  --proto "$PROTO_PATH" \
  --call usersorders.UserService.GetUsers \
  --insecure \
  --concurrency 10 \
  --duration 30s \
  ${GRPC_API_URL} \
  --format json > results/grpc/load_test_10vu.json

# Тест с 50 пользователями
ghz \
  --proto "$PROTO_PATH" \
  --call usersorders.UserService.GetUsers \
  --insecure \
  --concurrency 50 \
  --duration 30s \
  ${GRPC_API_URL} \
  --format json > results/grpc/load_test_50vu.json

echo "Тест поведения под нагрузкой для gRPC завершен."

# Проверка наличия утилиты grpcurl
if ! command -v grpcurl &> /dev/null; then
  echo "ОШИБКА: Утилита grpcurl не установлена"
  echo "Пропуск тестов, требующих grpcurl"
  exit 1
fi

# Тест на получение заказов
echo "Запуск теста получения заказов для gRPC..."

# Сначала создаем тестовые данные - пользователя
echo "Создание тестового пользователя..."
USER_ID=$(grpcurl -plaintext -d '{"name": "Test User", "email": "test@example.com"}' \
  ${GRPC_API_URL} usersorders.UserService/CreateUser | grep -o '"id": [0-9]*' | grep -o '[0-9]*')

if [ -z "$USER_ID" ]; then
  echo "ОШИБКА: Не удалось создать тестового пользователя"
  exit 1
fi

echo "Создан пользователь с ID: $USER_ID"

# Теперь создаем заказ для этого пользователя
echo "Создание тестового заказа..."
grpcurl -plaintext -d "{\"user_id\": $USER_ID, \"product_name\": \"Test Product\", \"price\": 99.99}" \
  ${GRPC_API_URL} usersorders.OrderService/CreateOrder

# Тестируем получение заказов пользователя
echo "Тестирование получения заказов пользователя..."
ghz \
  --proto "$PROTO_PATH" \
  --call usersorders.OrderService.GetOrdersByUser \
  --insecure \
  --total 100 \
  --concurrency 10 \
  --data "{\"id\": $USER_ID}" \
  ${GRPC_API_URL} \
  --format json > results/grpc/orders_by_user_test.json

echo "Тест получения заказов для gRPC завершен."

echo "Все тесты gRPC завершены. Результаты сохранены в директории results/grpc/"