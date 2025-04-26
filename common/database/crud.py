from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from typing import List, Optional, TypeVar, Generic, Type
from common.models.models import User, Order

# Создаем обобщенный тип для моделей
T = TypeVar('T')

class BaseCRUD(Generic[T]):
    """Базовый класс для CRUD операций"""
    
    def __init__(self, model: Type[T]):
        self.model = model
    
    async def get_all(self, db: AsyncSession) -> List[T]:
        """Получить все записи"""
        result = await db.execute(select(self.model))
        return result.scalars().all()
    
    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[T]:
        """Получить запись по ID"""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()
    
    async def create(self, db: AsyncSession, **kwargs) -> T:
        """Создать новую запись"""
        obj = self.model(**kwargs)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj
    
    async def delete(self, db: AsyncSession, id: int) -> bool:
        """Удалить запись по ID"""
        obj = await self.get_by_id(db, id)
        if not obj:
            return False
        await db.delete(obj)
        await db.commit()
        return True

# Конкретные классы для работы с моделями
class UserCRUD(BaseCRUD[User]):
    """CRUD операции для модели User"""
    
    def __init__(self):
        super().__init__(User)

class OrderCRUD(BaseCRUD[Order]):
    """CRUD операции для модели Order"""
    
    def __init__(self):
        super().__init__(Order)
    
    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> List[Order]:
        """Получить заказы пользователя по ID пользователя"""
        result = await db.execute(select(Order).where(Order.user_id == user_id))
        return result.scalars().all()

# Создаем экземпляры для использования
user_crud = UserCRUD()
order_crud = OrderCRUD()