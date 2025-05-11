from fastapi import FastAPI, Request
from app.routes import users_router, orders_router
from app.middleware import LoggingMiddleware
from common.models.base import Base
from common.database.connection import engine
from common.utils.logging import get_logger
import os

# Настройка логирования
logger = get_logger("rest_api", "rest_api.log")

app = FastAPI(title="REST API для сравнительного анализа")

# Подключаем middleware
app.add_middleware(LoggingMiddleware)

# Подключаем маршруты
app.include_router(users_router)
app.include_router(orders_router)

# Создаем таблицы при запуске приложения
@app.on_event("startup")
async def init_db():
    logger.info("Initializing database...")
    async with engine.begin() as conn:
        # Раскомментируйте следующую строку, чтобы сбросить базу при каждом запуске
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")

# Корневой маршрут
@app.get("/")
async def root():
    logger.debug("Root endpoint called")
    return {"message": "REST API для сравнительного анализа API технологий"}

# Маршрут для проверки здоровья сервиса
@app.get("/health")
async def health_check():
    logger.debug("Health check endpoint called")
    return {"status": "healthy"}

# Обработчик исключений
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=exc)
    return {"detail": "Internal server error"}