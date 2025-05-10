from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from common.database.crud import user_crud
from common.models.models import User
from .exceptions import NotFoundError, AlreadyExistsError, ValidationError
import re

class UserService:
    """Сервис для работы с пользователями"""
    
    # Простой regex для валидации email
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    async def get_all(self, db: AsyncSession):
        """Получить всех пользователей"""
        return await user_crud.get_all(db)
    
    async def get_by_id(self, db: AsyncSession, user_id: int):
        """Получить пользователя по ID"""
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            raise NotFoundError("User", user_id)
        return user
    
    async def get_by_email(self, db: AsyncSession, email: str):
        """Получить пользователя по email"""
        # Расширяем функционал CRUD, реализуя новый метод
        query = db.query(User).filter(User.email == email)
        result = await db.execute(query)
        user = result.scalars().first()
        return user
    
    async def create(self, db: AsyncSession, name: str, email: str):
        """Создать нового пользователя"""
        # Валидация email
        if not self.validate_email(email):
            raise ValidationError(f"Invalid email format: {email}")
        
        # Проверка на существование пользователя с таким email
        existing_user = await self.get_by_email(db, email)
        if existing_user:
            raise AlreadyExistsError("User", "email", email)
        
        try:
            return await user_crud.create(db, name=name, email=email)
        except IntegrityError as e:
            # Обработка ошибок уникальности
            if "unique constraint" in str(e).lower() and "email" in str(e).lower():
                raise AlreadyExistsError("User", "email", email)
            raise
    
    async def delete(self, db: AsyncSession, user_id: int):
        """Удалить пользователя"""
        # Проверяем существование пользователя
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        # Удаляем пользователя
        await db.delete(user)
        await db.commit()
        return True
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        return bool(self.EMAIL_REGEX.match(email))
    
    def validate_name(self, name: str) -> bool:
        """Validate user name"""
        return bool(name and name.strip())