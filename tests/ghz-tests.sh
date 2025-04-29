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

# Переменные для хранения идентификаторов тестовых данных
TEST_USER_IDS=()
TEST_ORDER_IDS=()

# Функция для удаления тестовых данных
cleanup_test_data() {
  echo "Очистка тестовых данных..."
  
  # Удаление тестовых заказов
  for order_id in "${TEST_ORDER_IDS[@]}"; do
    echo "Удаление заказа с ID: $order_id"
    grpcurl -plaintext -d "{\"id\": $order_id}" \
      ${GRPC_API_URL} usersorders.OrderService/DeleteOrder
  done
  
  # Удаление тестовых пользователей
  for user_id in "${TEST_USER_IDS[@]}"; do
    echo "Удаление пользователя с ID: $user_id"
    grpcurl -plaintext -d "{\"id\": $user_id}" \
      ${GRPC_API_URL} usersorders.UserService/DeleteUser
  done
  
  echo "Очистка тестовых данных завершена."
}

# Обработка сигналов для гарантированной очистки при прерывании
trap cleanup_test_data EXIT INT TERM

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

# Добавляем ID пользователя в массив для последующей очистки
TEST_USER_IDS+=($USER_ID)

echo "Создан пользователь с ID: $USER_ID"

# Теперь создаем заказ для этого пользователя
echo "Создание тестового заказа..."
ORDER_ID=$(grpcurl -plaintext -d "{\"user_id\": $USER_ID, \"product_name\": \"Test Product\", \"price\": 99.99}" \
  ${GRPC_API_URL} usersorders.OrderService/CreateOrder | grep -o '"id": [0-9]*' | grep -o '[0-9]*')

if [ -n "$ORDER_ID" ]; then
  # Добавляем ID заказа в массив для последующей очистки
  TEST_ORDER_IDS+=($ORDER_ID)
  echo "Создан заказ с ID: $ORDER_ID"
fi

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

# Создаем еще несколько тестовых пользователей и заказов для нагрузочного тестирования
for i in {1..5}; do
  echo "Создание дополнительного тестового пользователя $i..."
  USER_ID=$(grpcurl -plaintext -d "{\"name\": \"Load Test User $i\", \"email\": \"loadtest$i@example.com\"}" \
    ${GRPC_API_URL} usersorders.UserService/CreateUser | grep -o '"id": [0-9]*' | grep -o '[0-9]*')
  
  if [ -n "$USER_ID" ]; then
    TEST_USER_IDS+=($USER_ID)
    echo "Создан пользователь с ID: $USER_ID"
    
    # Создаем несколько заказов для этого пользователя
    for j in {1..3}; do
      ORDER_ID=$(grpcurl -plaintext -d "{\"user_id\": $USER_ID, \"product_name\": \"Load Test Product $j\", \"price\": $((50 + $j * 10))}" \
        ${GRPC_API_URL} usersorders.OrderService/CreateOrder | grep -o '"id": [0-9]*' | grep -o '[0-9]*')
      
      if [ -n "$ORDER_ID" ]; then
        TEST_ORDER_IDS+=($ORDER_ID)
        echo "Создан заказ с ID: $ORDER_ID для пользователя $USER_ID"
      fi
done

echo "Все тесты gRPC завершены. Результаты сохранены в директории results/grpc/"

# Очистка тестовых данных выполняется автоматически благодаря trap
    done
  fi