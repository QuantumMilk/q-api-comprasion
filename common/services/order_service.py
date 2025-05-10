# common/services/order_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from common.database.crud import order_crud, user_crud
from common.models.models import Order
from .exceptions import NotFoundError, ValidationError
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

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
        """Create a new order"""
        # Check user existence
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        # Price validation
        try:
            # Convert to Decimal for precision
            decimal_price = Decimal(str(price))
            
            # Validate positive price
            if decimal_price <= 0:
                raise ValidationError("Price must be greater than zero")
            
            # Limit to 2 decimal places
            decimal_price = decimal_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # Check if price has more than 10 significant digits
            if len(decimal_price.as_tuple().digits) > 10:
                raise ValidationError("Price is too large, maximum 10 digits allowed")
                
        except InvalidOperation:
            raise ValidationError(f"Invalid price format: {price}")
        
        # Product name validation
        if not product_name or not product_name.strip():
            raise ValidationError("Product name cannot be empty")
        
        if len(product_name) > 255:
            raise ValidationError("Product name is too long, maximum 255 characters allowed")
        
        try:
            return await order_crud.create(
                db, 
                user_id=user_id, 
                product_name=product_name, 
                price=decimal_price
            )
        except IntegrityError as e:
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