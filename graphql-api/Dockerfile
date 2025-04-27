FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY ./graphql-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY ./graphql-api/app /app/app
COPY ./common /app/common

# Порт для GraphQL API
EXPOSE 8080

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]