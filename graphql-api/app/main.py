from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from app.graphql.schema import schema
from common.models.base import Base
from common.database.connection import engine
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
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
    logger.info("База данных инициализирована")

# Корневой маршрут
@app.get("/")
async def root():
    return {"message": "GraphQL API для сравнительного анализа API технологий. Перейдите к /graphql для доступа к GraphQL Playground"}