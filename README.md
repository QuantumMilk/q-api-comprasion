# Сравнение API технологий: REST vs GraphQL vs gRPC

[![API Comparison CI/CD](https://github.com/QuantumMilk/q-api-comprasion/actions/workflows/api-comparison-workflow.yml/badge.svg)](https://github.com/QuantumMilk/q-api-comprasion/actions/workflows/api-comparison-workflow.yml)

Проект для сравнения характеристик производительности трех популярных технологий API: REST, GraphQL и gRPC. Этот репозиторий содержит код и тесты для измерения и сравнения задержки, пропускной способности и поведения под нагрузкой для каждого типа API.

## Архитектура проекта

Проект состоит из трех основных API, реализованных с использованием разных технологий, все они взаимодействуют с одной и той же базой данных PostgreSQL:

- **REST API** - реализован с использованием FastAPI
- **GraphQL API** - реализован с использованием Strawberry GraphQL и FastAPI
- **gRPC API** - реализован с использованием gRPC и Protocol Buffers

## CI/CD интеграция

Проект настроен для непрерывной интеграции и доставки с использованием GitHub Actions. Автоматизированный процесс включает:

1. **Сборка и валидация** - проверка кода, линтинг и статический анализ
2. **Тестирование API** - запуск сравнительных тестов производительности
3. **Генерация отчетов** - создание HTML-отчетов на основе результатов тестирования
4. **Публикация отчетов** - автоматическая публикация отчетов на GitHub Pages

### Процесс CI/CD

![CI/CD процесс](https://mermaid.ink/img/pako:eNptkU9rAjEQxb_KMKcW9kAP9tCL9FBKDxVaL2UvYzIxwWyyJLNKKft_VzfWQuszw8z7vQfJC2pnCSvs0D0bnYObXbIYp7fHMPxYVnmG0JI_wvOtNsON1QNcCCpzNKQI-v3sEfb7L9jl4oJWD6QEXvHbdIYBG6xCGq1Dh3BzjpXgLDUGMU02FDIEe9LtYfcfsytNsWlZc8QOHYr-sSP-I5fUkbD7nh4kxaklKTgmSgHbIcnUQyP3aQ-MQvnuV6zqfDBGVXbvKpqCSd4V6uLUuUkV1_9ZLZrSq9D5XtXaDDldXqy45qBbDfEkM5YuJTjzLRvMmAXGb-7GnLKh_dQzVkH06_9lnqtSjTMsZjm52rba6jmrq7PQAGdQ7oEqB9jn65MqHgw)

### Запуск CI/CD

CI/CD процесс запускается автоматически при:

- Push в ветки `main`, `master` или `develop`
- Pull Request в ветки `main` или `master`
- Ручном запуске через GitHub Actions интерфейс

## Настройка GitHub Actions

1. **Форкните или клонируйте** этот репозиторий в свой GitHub аккаунт
2. Перейдите в **Settings > Pages** и выберите источником ветку `gh-pages`
3. Для ручного запуска тестов:
   - Перейдите в **Actions** > **API Comparison CI/CD**
   - Нажмите **Run workflow**
   - Выберите ветку и параметры запуска
   - Подтвердите запуск кнопкой **Run workflow**

## Просмотр результатов

После успешного выполнения workflow результаты автоматически публикуются на GitHub Pages:

- Отчеты о производительности: `https://QuantumMilk.github.io/q-api-comprasion/`
- Графики: `https://QuantumMilk.github.io/q-api-comprasion/graphs/`

## Локальный запуск

Вы также можете запустить тесты локально:

```bash
# Клонируйте репозиторий
git clone https://github.com/QuantumMilk/q-api-comprasion.git
cd api-comparison

# Запустите сервисы с использованием Docker Compose
docker-compose up -d

# Запустите тесты
docker-compose run --rm tests bash
cd /tests
chmod +x run-tests.sh
./run-tests.sh

# Отчеты и графики будут доступны в директории ./results/
```

## Настройка CI/CD для собственного проекта

Если вы хотите использовать эту CI/CD конфигурацию для собственного проекта:

1. Скопируйте файлы из директории `.github/` в свой проект
2. Адаптируйте `api-comparison-workflow.yml` под свои нужды:
   - Измените триггеры запуска (ветки, события)
   - Настройте шаги сборки и тестирования
   - Настройте деплой отчетов

## Метрики и параметры тестирования

Тестирование API включает измерение следующих метрик:

- **Задержка (Latency)** - время отклика на запрос
- **Пропускная способность (Throughput)** - количество обрабатываемых запросов в секунду
- **Поведение под нагрузкой (Load)** - как меняется время отклика при увеличении нагрузки
- **Стабильность (Stability)** - насколько стабильны показатели при продолжительной работе

Тесты проводятся с различным количеством виртуальных пользователей (VU):
- 1 VU - базовый тест производительности без нагрузки
- 10 VU - средняя нагрузка
- 50 VU - высокая нагрузка

