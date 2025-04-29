.PHONY: build up down test deploy clean healthcheck

# Переменные
DOCKER_COMPOSE = docker-compose

# Базовые команды для разработки
build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

# Запуск всех тестов
test:
	$(DOCKER_COMPOSE) run --rm tests bash -c "cd /tests && chmod +x run-tests.sh && ./run-tests.sh"

# Запуск только конкретных тестов
test-rest:
	$(DOCKER_COMPOSE) run --rm tests k6 run /tests/k6-scripts/rest_latency_test.js --out json=/tests/results/rest/latency_test.json

test-graphql:
	$(DOCKER_COMPOSE) run --rm tests k6 run /tests/k6-scripts/graphql_latency_test.js --out json=/tests/results/graphql/latency_test.json

test-grpc:
	$(DOCKER_COMPOSE) run --rm tests bash -c "cd /tests && chmod +x ghz-tests.sh && ./ghz-tests.sh"

# Для деплоя
deploy:
	chmod +x deploy.sh && ./deploy.sh

# Проверка состояния API
healthcheck:
	RUN_HEALTHCHECK=true ./deploy.sh

# Очистка ресурсов
clean:
	$(DOCKER_COMPOSE) down -v
	rm -rf results/*

# Вывод справочной информации
help:
	@echo "Доступные команды:"
	@echo "  make build        - Собрать все Docker образы"
	@echo "  make up           - Запустить все сервисы"
	@echo "  make down         - Остановить все сервисы"
	@echo "  make test         - Запустить все тесты"
	@echo "  make test-rest    - Запустить только тесты REST API"
	@echo "  make test-graphql - Запустить только тесты GraphQL API"
	@echo "  make test-grpc    - Запустить только тесты gRPC API"
	@echo "  make deploy       - Развернуть приложение"
	@echo "  make healthcheck  - Проверить работоспособность всех API"
	@echo "  make clean        - Очистить ресурсы и результаты тестов"