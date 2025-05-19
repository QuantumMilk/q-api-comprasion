#!/bin/bash
set -e

# Проверяем переменные SSL
if [ "$SSL_ENABLED" = "true" ]; then
    echo "Запуск REST API с поддержкой SSL на порту 8443..."
    uvicorn app.main:app --host 0.0.0.0 --port 8443 --ssl-keyfile $SSL_KEY_PATH --ssl-certfile $SSL_CERT_PATH --reload
else
    echo "Запуск REST API без SSL на порту 8000..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi