from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from app.graphql.schema import schema
from common.models.base import Base
from common.database.connection import engine
import logging
import os
from logging.handlers import RotatingFileHandler

# Создание директории для логов, если она не существует
os.makedirs('/app/logs', exist_ok=True)

# Настройка логирования
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Вывод в консоль
        RotatingFileHandler(
            '/app/logs/app.log',
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5                # 5 резервных копий
        )
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="GraphQL API для сравнительного анализа")

# Создаем роутер GraphQL
graphql_app = GraphQLRouter(schema)

# Подключаем GraphQL-маршрут
app.include_router(graphql_app, prefix="/graphql")

# Создаем таблицы при запуске приложения
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        # Раскомментируйте следующую строку, чтобы сбросить базу при каждом запуске
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")

# Корневой маршрут
@app.get("/")
async def root():
    return {"message": "GraphQL API для сравнительного анализа API технологий. Перейдите к /graphql для доступа к GraphQL Playground"}

# Маршрут для проверки здоровья сервиса
@app.get("/health")
async def health_check():
    return {"status": "healthy"}