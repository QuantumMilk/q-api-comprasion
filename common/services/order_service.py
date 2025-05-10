# common/services/order_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from common.database.crud import order_crud, user_crud
from common.models.models import Order
from .exceptions import NotFoundError, ValidationError
from decimal import Decimal, InvalidOperation

class OrderService:
    """Сервис для работы с заказами"""
    
    async def get_all(self, db: AsyncSession):
        """Получить все заказы"""
        return await order_crud.get_all(db)
    
    async def get_by_id(self, db: AsyncSession, order_id: int):
        """Получить заказ по ID"""
        order = await order_crud.get_by_id(db, order_id)
        if not order:
            raise NotFoundError("Order", order_id)
        return order
    
    async def get_by_user_id(self, db: AsyncSession, user_id: int):
        """Получить заказы пользователя"""
        # Проверяем существование пользователя
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        return await order_crud.get_by_user_id(db, user_id)
    
    async def create(self, db: AsyncSession, user_id: int, product_name: str, price):
        """Создать новый заказ"""
        # Проверяем существование пользователя
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        # Валидация цены
        try:
            # Преобразуем к Decimal для точности
            decimal_price = Decimal(str(price))
            if decimal_price <= 0:
                raise ValidationError("Price must be greater than zero")
            
            # Ограничиваем до 2 знаков после запятой
            decimal_price = decimal_price.quantize(Decimal('0.01'))
        except InvalidOperation:
            raise ValidationError(f"Invalid price format: {price}")
        
        # Валидация названия продукта
        if not product_name or len(product_name) < 1:
            raise ValidationError("Product name cannot be empty")
        
        try:
            return await order_crud.create(
                db, 
                user_id=user_id, 
                product_name=product_name, 
                price=decimal_price
            )
        except IntegrityError as e:
            # Обработка других ошибок базы данных
            raise ValidationError(f"Database error: {str(e)}")
    
    async def delete(self, db: AsyncSession, order_id: int):
        """Удалить заказ"""
        # Проверяем существование заказа
        order = await order_crud.get_by_id(db, order_id)
        if not order:
            raise NotFoundError("Order", order_id)
        
        # Удаляем заказ
        await db.delete(order)
        await db.commit()
        return True