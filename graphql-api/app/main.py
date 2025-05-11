from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter
from app.graphql.schema import schema
from app.middleware import LoggingMiddleware
from common.models.base import Base
from common.database.connection import engine
from common.utils.logging import get_logger
import os

# Настройка логирования
logger = get_logger("graphql_api", "graphql_api.log")

app = FastAPI(title="GraphQL API для сравнительного анализа")

# Подключаем middleware
app.add_middleware(LoggingMiddleware)

# Создаем роутер GraphQL
graphql_app = GraphQLRouter(schema)

# Подключаем GraphQL-маршрут
app.include_router(graphql_app, prefix="/graphql")

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
    return {"message": "GraphQL API для сравнительного анализа API технологий. Перейдите к /graphql для доступа к GraphQL Playground"}

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