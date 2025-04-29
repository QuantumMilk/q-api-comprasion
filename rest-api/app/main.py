from fastapi import FastAPI
from app.routes import users_router, orders_router
from common.models.base import Base
from common.database.connection import engine
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

app = FastAPI(title="REST API для сравнительного анализа")

# Подключаем маршруты
app.include_router(users_router)
app.include_router(orders_router)

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
    return {"message": "REST API для сравнительного анализа API технологий"}