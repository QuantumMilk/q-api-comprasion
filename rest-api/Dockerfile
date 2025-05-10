FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY ./rest-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY ./rest-api/app /app/app
COPY ./common /app/common

# Создаем директорию для логов
RUN mkdir -p /app/logs

# Аргумент для переключения режима запуска
ARG ENVIRONMENT=development

# Запуск приложения в зависимости от режима
CMD if [ "$ENVIRONMENT" = "development" ]; then \
      uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload; \
    else \
      uvicorn app.main:app --host 0.0.0.0 --port 8000; \
    fi