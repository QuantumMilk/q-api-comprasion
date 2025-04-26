import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Получаем параметры подключения из переменных окружения
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "db")  # Имя сервиса в docker-compose
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "postgres")

# Строка подключения к базе данных
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создаем движок для работы с базой данных
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем фабрику сессий
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Функция для получения сессии
async def get_db():
    async with async_session() as session:
        yield session