# Сравнение API

docker-compose run --rm tests bash

# Внутри контейнера
cd /tests
chmod +x run-tests.sh
./run-tests.sh

# Или запускать отдельные тесты
k6 run k6-scripts/rest_latency_test.js --out json=results/rest/latency_test.json

## Структура проекта

- `common/` - общий код для всех API
- `rest-api/` - реализация REST API
- `graphql-api/` - реализация GraphQL API
- `grpc-api/` - реализация gRPC API
- `tests/` - тесты производительности

## Запуск приложения

### С помощью скрипта

Запустить определенный API:

```bash
./run-api.sh rest     # Запуск REST API
./run-api.sh graphql  # Запуск GraphQL API
./run-api.sh grpc     # Запуск gRPC API
./run-api.sh all      # Запуск всех API


С использованием Docker Compose
Запустить все сервисы:
bashdocker-compose --profile full up -d
Запустить только определенный API:
bashdocker-compose --profile rest up -d
docker-compose --profile graphql up -d
docker-compose --profile grpc up -d
Запуск тестов производительности
bashdocker-compose --profile test up
Или для запуска отдельных тестов:
bashdocker-compose run --rm tests bash
cd /tests
chmod +x run-tests.sh
./run-tests.sh
Для запуска конкретного теста:
bashdocker-compose run --rm tests bash
cd /tests
k6 run k6-scripts/rest_latency_test.js --out json=results/rest/latency_test.json


## Логирование

В проекте настроено структурированное логирование различных событий:

- Запросы API (HTTP и gRPC)
- Бизнес-события (создание/удаление пользователей и заказов)
- Ошибки и исключения

### Просмотр логов

Для просмотра логов можно использовать скрипт:

```bash
./view-logs.sh rest        # Просмотр логов REST API
./view-logs.sh graphql     # Просмотр логов GraphQL API
./view-logs.sh grpc        # Просмотр логов gRPC API
./view-logs.sh all         # Просмотр всех логов

# Опции
./view-logs.sh rest -f                 # Следить за логами в реальном времени
./view-logs.sh graphql -n 100          # Показать последние 100 строк
./view-logs.sh grpc -s business        # Показать логи бизнес-событий gRPC API