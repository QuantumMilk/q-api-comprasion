from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from common.database.crud import user_crud
from common.models.models import User
from common.utils.logging import get_logger, log_business_event, log_exception
from .exceptions import NotFoundError, AlreadyExistsError, ValidationError
import re

logger = get_logger(__name__, "user_service.log")

class UserService:
    """Сервис для работы с пользователями"""
    
    # Простой regex для валидации email
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    async def get_all(self, db: AsyncSession):
        """Получить всех пользователей"""
        logger.info("Retrieving all users")
        users = await user_crud.get_all(db)
        logger.info(f"Retrieved {len(users)} users")
        return users
    
    async def get_by_id(self, db: AsyncSession, user_id: int):
        """Получить пользователя по ID"""
        logger.info(f"Retrieving user by ID: {user_id}")
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            raise NotFoundError("User", user_id)
        logger.info(f"Retrieved user with ID: {user_id}")
        return user
    
    async def get_by_email(self, db: AsyncSession, email: str):
        """Получить пользователя по email"""
        logger.info(f"Retrieving user by email: {email}")
        # Расширяем функционал CRUD, реализуя новый метод
        query = db.query(User).filter(User.email == email)
        result = await db.execute(query)
        user = result.scalars().first()
        if user:
            logger.info(f"Retrieved user with email: {email}, ID: {user.id}")
        else:
            logger.info(f"No user found with email: {email}")
        return user
    
    async def create(self, db: AsyncSession, name: str, email: str):
        """Создать нового пользователя"""
        logger.info(f"Creating new user with name: {name}, email: {email}")
        
        # Валидация email
        if not self.validate_email(email):
            logger.warning(f"Invalid email format: {email}")
            raise ValidationError(f"Invalid email format: {email}")
        
        # Проверка на существование пользователя с таким email
        existing_user = await self.get_by_email(db, email)
        if existing_user:
            logger.warning(f"User with email {email} already exists")
            raise AlreadyExistsError("User", "email", email)
        
        try:
            user = await user_crud.create(db, name=name, email=email)
            logger.info(f"Created new user with ID: {user.id}")
            log_business_event(logger, "created", "user", user.id, {"name": name, "email": email})
            return user
        except IntegrityError as e:
            # Обработка ошибок уникальности
            log_exception(logger, e, {"name": name, "email": email})
            if "unique constraint" in str(e).lower() and "email" in str(e).lower():
                logger.warning(f"User with email {email} already exists (caught by DB constraint)")
                raise AlreadyExistsError("User", "email", email)
            raise
    
    async def delete(self, db: AsyncSession, user_id: int):
        """Удалить пользователя"""
        logger.info(f"Deleting user with ID: {user_id}")
        # Проверяем существование пользователя
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            logger.warning(f"Cannot delete: User with ID {user_id} not found")
            raise NotFoundError("User", user_id)
        
        # Удаляем пользователя
        await db.delete(user)
        await db.commit()
        logger.info(f"User with ID {user_id} deleted successfully")
        log_business_event(logger, "deleted", "user", user_id)
        return True
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        return bool(self.EMAIL_REGEX.match(email))
    
    def validate_name(self, name: str) -> bool:
        """Validate user name"""
        return bool(name and name.strip())