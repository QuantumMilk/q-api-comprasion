from .user_service import UserService
from .order_service import OrderService
from .exceptions import (
    NotFoundError,
    ValidationError,
    AlreadyExistsError,
    ServiceError
)

# Создаем экземпляры сервисов для использования в API
user_service = UserService()
order_service = OrderService()