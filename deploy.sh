#!/bin/bash
# Скрипт для деплоя приложения на сервер

set -e  # Завершить скрипт при ошибке

# Переменные окружения (могут быть переопределены через переменные окружения CI)
DEPLOY_ENV=${DEPLOY_ENV:-"production"}
DB_PASSWORD=${DB_PASSWORD:-"postgres"}
APP_PORT=${APP_PORT:-"8000"}
GRAPHQL_PORT=${GRAPHQL_PORT:-"8080"}
GRPC_PORT=${GRPC_PORT:-"50051"}

echo "Развертывание в окружении: $DEPLOY_ENV"

# Создаем файл .env для переменных окружения Docker Compose
cat > .env << EOF
POSTGRES_USER=postgres
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_DB=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
EOF

# Обновляем код из репозитория, если скрипт запущен не из CI
if [ -z "$CI" ]; then
  echo "Обновление кода из репозитория..."
  git pull
fi

# Запуск сервисов с пробросом нужных портов
echo "Запуск сервисов..."
docker-compose down
docker-compose build
docker-compose up -d db

echo "Ждем запуска базы данных..."
sleep 10

# Запускаем API
echo "Запускаем API сервисы..."
docker-compose up -d rest-api graphql-api grpc-api

echo "Приложение успешно развернуто!"
echo "REST API доступен на порту: $APP_PORT"
echo "GraphQL API доступен на порту: $GRAPHQL_PORT"
echo "gRPC API доступен на порту: $GRPC_PORT"

# Опциональный запуск простых тестов для проверки работоспособности
if [ "$RUN_HEALTHCHECK" = "true" ]; then
  echo "Запуск проверки работоспособности..."
  sleep 5
  
  # Проверка REST API
  REST_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT)
  if [ "$REST_STATUS" = "200" ]; then
    echo "REST API работает."
  else
    echo "ОШИБКА: REST API не отвечает! (статус $REST_STATUS)"
  fi
  
  # Проверка GraphQL API
  GRAPHQL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$GRAPHQL_PORT)
  if [ "$GRAPHQL_STATUS" = "200" ]; then
    echo "GraphQL API работает."
  else
    echo "ОШИБКА: GraphQL API не отвечает! (статус $GRAPHQL_STATUS)"
  fi
  
  # Для gRPC мы можем только проверить, открыт ли порт
  if nc -z localhost $GRPC_PORT; then
    echo "gRPC API порт доступен."
  else
    echo "ОШИБКА: gRPC API порт недоступен!"
  fi
fi