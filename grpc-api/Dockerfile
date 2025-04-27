FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY ./grpc-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY ./grpc-api/app /app/app
COPY ./grpc-api/client.py /app/client.py
COPY ./grpc-api/entrypoint.sh /app/entrypoint.sh
COPY ./common /app/common

# Делаем скрипт исполняемым
RUN chmod +x /app/entrypoint.sh

# Порт для gRPC
EXPOSE 50051

# Запуск через entrypoint скрипт
CMD ["/app/entrypoint.sh"]