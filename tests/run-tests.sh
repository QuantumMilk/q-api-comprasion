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
k6 run k6-scripts/rest_load_test.js --out json=results/rest/load_test.json

echo "==================================="
echo "Запуск тестов GraphQL API"
echo "==================================="

echo "Запуск теста задержки для GraphQL API..."
k6 run k6-scripts/graphql_latency_test.js --out json=results/graphql/latency_test.json

echo "Запуск теста пропускной способности для GraphQL API..."
k6 run k6-scripts/graphql_throughput_test.js --out json=results/graphql/throughput_test.json