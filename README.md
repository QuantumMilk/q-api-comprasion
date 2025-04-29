# Сравнение API

docker-compose run --rm tests bash

# Внутри контейнера
cd /tests
chmod +x run-tests.sh
./run-tests.sh

# Или запускать отдельные тесты
k6 run k6-scripts/rest_latency_test.js --out json=results/rest/latency_test.json


===

# CI/CD для проекта сравнения API

Это руководство описывает настройку CI/CD для проекта сравнения API (REST, GraphQL, gRPC).

## Обзор CI/CD процесса

CI/CD пайплайн автоматизирует:
1. **Сборку** - создание Docker-образов для всех сервисов
2. **Тестирование** - запуск тестов на производительность и функциональность
3. **Развертывание** - автоматическое развертывание приложения на сервере

## Структура CI/CD

Репозиторий содержит следующие файлы для CI/CD:
- `.github/workflows/main.yml` - основной CI пайплайн для сборки и тестирования
- `.github/workflows/deploy.yml` - пайплайн для автоматического деплоя на сервер
- `deploy.sh` - скрипт для деплоя приложения
- `Makefile` - утилиты для локального управления проектом

## Настройка GitHub Actions

1. Перейдите в репозиторий на GitHub
2. Выберите вкладку "Settings"
3. Перейдите в раздел "Secrets and variables" -> "Actions"
4. Добавьте следующие секреты для деплоя:
   - `SSH_PRIVATE_KEY` - приватный SSH-ключ для доступа к серверу
   - `SERVER_HOST` - IP-адрес или имя хоста сервера
   - `SERVER_USER` - имя пользователя для SSH подключения
   - `DEPLOY_PATH` - путь на сервере для деплоя
   - `DB_PASSWORD` - пароль для базы данных

## Локальное использование CI/CD инструментов

### Основные команды Makefile

```
make build       # Собрать все Docker образы
make up          # Запустить все сервисы
make down        # Остановить все сервисы
make test        # Запустить все тесты
make deploy      # Развернуть приложение
make healthcheck # Проверить работоспособность API
make clean       # Очистить ресурсы и результаты тестов
```

### Запуск отдельных тестов

```
make test-rest     # Тесты только REST API
make test-graphql  # Тесты только GraphQL API
make test-grpc     # Тесты только gRPC API
```

## Ручной деплой

Для ручного развертывания на сервере:

1. Скопируйте проект на сервер:
   ```
   rsync -avz --exclude 'node_modules' --exclude '.git' --exclude 'results' ./ user@server:/path/to/deploy
   ```

2. Выполните скрипт деплоя:
   ```
   ssh user@server "cd /path/to/deploy && chmod +x deploy.sh && ./deploy.sh"
   ```

## Проверка работоспособности

После деплоя проверьте, что все API доступны:

```
make healthcheck
```

Или вручную проверьте доступность:
- REST API: http://server:8000
- GraphQL API: http://server:8080/graphql
- gRPC API через gRPC клиент на порту 50051

## Мониторинг деплоя

Журналы работы всех сервисов можно проверить с помощью:

```
docker-compose logs -f
```

Для проверки отдельного сервиса:

```
docker-compose logs -f rest-api
docker-compose logs -f graphql-api
docker-compose logs -f grpc-api
```