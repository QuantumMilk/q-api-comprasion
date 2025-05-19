#!/bin/bash
set -e

# Проверяем переменные SSL
if [ "$SSL_ENABLED" = "true" ]; then
    echo "Запуск GraphQL API с поддержкой SSL на порту 8444..."
    uvicorn app.main:app --host 0.0.0.0 --port 8444 --ssl-keyfile $SSL_KEY_PATH --ssl-certfile $SSL_CERT_PATH --reload
else
    echo "Запуск GraphQL API без SSL на порту 8080..."
    uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
fi