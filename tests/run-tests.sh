#!/bin/bash

# Функция для логирования
log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Функция для обработки ошибок
handle_error() {
  log "ОШИБКА: $1"
  exit 1
}

# Создаем директории для результатов
mkdir -p results/rest
mkdir -p results/graphql
mkdir -p results/grpc
mkdir -p results/graphs

log "====================================="
log "Запуск тестов REST API"
log "====================================="

log "Запуск теста задержки для REST API..."
k6 run k6-scripts/rest_latency_test.js --out json=results/rest/latency_test.json || handle_error "Не удалось выполнить тест задержки REST API"

log "Запуск теста пропускной способности для REST API..."
k6 run k6-scripts/rest_throughput_test.js --out json=results/rest/throughput_test.json || handle_error "Не удалось выполнить тест пропускной способности REST API"

log "Запуск теста поведения под нагрузкой для REST API..."
# Этап 1: 1 VU
k6 run --env STAGE=1 --stage 30s:1 k6-scripts/rest_load_test.js --out json=results/rest/load_test_stage1.json || log "Предупреждение: Проблема при выполнении теста нагрузки REST API (этап 1)"
# Этап 2: 10 VU
k6 run --env STAGE=2 --stage 30s:10 k6-scripts/rest_load_test.js --out json=results/rest/load_test_stage2.json || log "Предупреждение: Проблема при выполнении теста нагрузки REST API (этап 2)"
# Этап 3: 50 VU
k6 run --env STAGE=3 --stage 30s:50 k6-scripts/rest_load_test.js --out json=results/rest/load_test_stage3.json || log "Предупреждение: Проблема при выполнении теста нагрузки REST API (этап 3)"


log "====================================="
log "Запуск тестов GraphQL API"
log "====================================="

log "Запуск теста задержки для GraphQL API..."
k6 run k6-scripts/graphql_latency_test.js --out json=results/graphql/latency_test.json || handle_error "Не удалось выполнить тест задержки GraphQL API"

log "Запуск теста пропускной способности для GraphQL API..."
k6 run k6-scripts/graphql_throughput_test.js --out json=results/graphql/throughput_test.json || handle_error "Не удалось выполнить тест пропускной способности GraphQL API"

log "Запуск теста поведения под нагрузкой для GraphQL API..."
# Этап 1: 1 VU
k6 run --env STAGE=1 --stage 30s:1 k6-scripts/graphql_load_test.js --out json=results/graphql/load_test_stage1.json || log "Предупреждение: Проблема при выполнении теста нагрузки GraphQL API (этап 1)"
# Этап 2: 10 VU
k6 run --env STAGE=2 --stage 30s:10 k6-scripts/graphql_load_test.js --out json=results/graphql/load_test_stage2.json || log "Предупреждение: Проблема при выполнении теста нагрузки GraphQL API (этап 2)"
# Этап 3: 50 VU
k6 run --env STAGE=3 --stage 30s:50 k6-scripts/graphql_load_test.js --out json=results/graphql/load_test_stage3.json || log "Предупреждение: Проблема при выполнении теста нагрузки GraphQL API (этап 3)"

log "Запуск теста overfetching для GraphQL API..."
k6 run k6-scripts/graphql_overfetching_test.js --out json=results/graphql/overfetching_test.json || log "Предупреждение: Проблема при выполнении теста overfetching GraphQL API"

# Запускаем тесты gRPC, если есть скрипт
log "====================================="
log "Запуск тестов gRPC API"
log "====================================="

if [ -f ./ghz-tests.sh ]; then
  chmod +x ./ghz-tests.sh
  ./ghz-tests.sh || log "Предупреждение: Проблемы при выполнении тестов gRPC API"
else
  log "Скрипт ghz-tests.sh не найден, пропуск тестов gRPC"
fi

# Запускаем анализ результатов
log "====================================="
log "Анализ результатов тестирования..."
log "====================================="

python3 analyze.py || log "Предупреждение: Проблемы при анализе результатов"

# Генерируем HTML-отчет
log "====================================="
log "Генерация HTML-отчета..."
log "====================================="

if [ -f ./generate_report.py ]; then
  python3 generate_report.py || log "Предупреждение: Проблемы при генерации HTML-отчета"
  log "HTML-отчет успешно сгенерирован"
else
  log "Скрипт generate_report.py не найден, пропуск генерации HTML-отчета"
fi

log "====================================="
log "Тестирование завершено"
log "====================================="