#!/bin/bash
set -e

echo "Генерация Python кода из .proto файла..."
python -m grpc_tools.protoc \
    --proto_path=/app/app/protos \
    --python_out=/app/app/protos \
    --grpc_python_out=/app/app/protos \
    /app/app/protos/service.proto

# Проверяем, что файлы созданы
if [ ! -f /app/app/protos/service_pb2.py ] || [ ! -f /app/app/protos/service_pb2_grpc.py ]; then
    echo "Ошибка: Файлы не были сгенерированы!"
    exit 1
fi

# Исправляем пути импорта в сгенерированных файлах
echo "Исправление путей импорта..."
sed -i 's/import service_pb2/from . import service_pb2/g' /app/app/protos/service_pb2_grpc.py

# Проверяем что __init__.py существует
touch /app/app/protos/__init__.py

echo "Инициализация завершена, запуск сервера..."
python -m app.main