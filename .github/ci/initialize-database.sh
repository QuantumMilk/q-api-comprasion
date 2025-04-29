#!/bin/bash

# Скрипт для инициализации базы данных в CI/CD окружении
# Заполняет базу тестовыми данными для корректного выполнения тестов

set -e

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log "Ожидание запуска и инициализации PostgreSQL..."
# Ожидаем 30 секунд, чтобы дать PostgreSQL время на запуск
sleep 30

# Проверяем, что база данных доступна
RETRIES=5
until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1" > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
  log "Ожидание запуска PostgreSQL... (осталось попыток: $RETRIES)"
  RETRIES=$((RETRIES-1))
  sleep 10
done

if [ $RETRIES -eq 0 ]; then
  log "Ошибка: не удалось подключиться к PostgreSQL"
  exit 1
fi

log "PostgreSQL успешно запущен. Заполняем тестовыми данными..."

# Заполняем базу тестовыми данными
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "
-- Создаем тестовых пользователей
INSERT INTO users (name, email, created_at) VALUES
  ('John Doe', 'john@example.com', NOW()),
  ('Jane Smith', 'jane@example.com', NOW()),
  ('Bob Johnson', 'bob@example.com', NOW()),
  ('Alice Brown', 'alice@example.com', NOW()),
  ('Charlie Davis', 'charlie@example.com', NOW())
ON CONFLICT (email) DO NOTHING;

-- Получаем ID созданных пользователей
WITH user_ids AS (SELECT id FROM users WHERE email IN ('john@example.com', 'jane@example.com', 'bob@example.com', 'alice@example.com', 'charlie@example.com'))

-- Создаем тестовые заказы
INSERT INTO orders (user_id, product_name, price, created_at)
SELECT 
  id,
  'Product ' || (random() * 100)::int::text,
  (random() * 1000)::numeric(10,2),
  NOW() - (random() * 30 || ' days')::interval
FROM user_ids, generate_series(1, 5)
ON CONFLICT DO NOTHING;
"

log "Инициализация базы данных завершена успешно"