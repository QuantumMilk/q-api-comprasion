#!/bin/bash

# Создаем директории для результатов
mkdir -p results/rest
mkdir -p results/graphql
mkdir -p results/grpc
mkdir -p results/graphs

echo "==================================="
echo "Запуск тестов REST API"
echo "==================================="

echo "Запуск теста задержки для REST API..."
k6 run k6-scripts/rest_latency_test.js --out json=results/rest/latency_test.json

echo "Запуск теста пропускной способности для REST API..."
k6 run k6-scripts/rest_throughput_test.js --out json=results/rest/throughput_test.json

echo "Запуск теста поведения под нагрузкой для REST API..."
# Этап 1: 1 VU
k6 run --env STAGE=1 --stage 30s:1 k6-scripts/rest_load_test.js --out json=results/rest/load_test_stage1.json
# Этап 2: 10 VU
k6 run --env STAGE=2 --stage 30s:10 k6-scripts/rest_load_test.js --out json=results/rest/load_test_stage2.json
# Этап 3: 50 VU
k6 run --env STAGE=3 --stage 30s:50 k6-scripts/rest_load_test.js --out json=results/rest/load_test_stage3.json


echo "==================================="
echo "Запуск тестов GraphQL API"
echo "==================================="

echo "Запуск теста задержки для GraphQL API..."
k6 run k6-scripts/graphql_latency_test.js --out json=results/graphql/latency_test.json

echo "Запуск теста пропускной способности для GraphQL API..."
k6 run k6-scripts/graphql_throughput_test.js --out json=results/graphql/throughput_test.json

echo "Запуск теста поведения под нагрузкой для GraphQL API..."
# Этап 1: 1 VU
k6 run --env STAGE=1 --stage 30s:1 k6-scripts/graphql_load_test.js --out json=results/graphql/load_test_stage1.json
# Этап 2: 10 VU
k6 run --env STAGE=2 --stage 30s:10 k6-scripts/graphql_load_test.js --out json=results/graphql/load_test_stage2.json
# Этап 3: 50 VU
k6 run --env STAGE=3 --stage 30s:50 k6-scripts/graphql_load_test.js --out json=results/graphql/load_test_stage3.json

echo "Запуск теста overfetching для GraphQL API..."
k6 run k6-scripts/graphql_overfetching_test.js --out json=results/graphql/overfetching_test.json

# Запускаем тесты gRPC, если они не запускаются
echo "Запуск тестов gRPC API..."
./ghz-tests.sh

# Запускаем анализ результатов
echo "Анализ результатов тестирования..."
python3 analyze.py