FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY ./rest-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY ./rest-api/app /app/app
COPY ./common /app/common

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]