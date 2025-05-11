from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from common.database.crud import order_crud, user_crud
from common.models.models import Order
from common.utils.logging import get_logger, log_business_event, log_exception
from .exceptions import NotFoundError, ValidationError
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

logger = get_logger(__name__, "order_service.log")

class OrderService:
    """Сервис для работы с заказами"""
    
    async def get_all(self, db: AsyncSession):
        """Получить все заказы"""
        logger.info("Retrieving all orders")
        orders = await order_crud.get_all(db)
        logger.info(f"Retrieved {len(orders)} orders")
        return orders
    
    async def get_by_id(self, db: AsyncSession, order_id: int):
        """Получить заказ по ID"""
        logger.info(f"Retrieving order by ID: {order_id}")
        order = await order_crud.get_by_id(db, order_id)
        if not order:
            logger.warning(f"Order with ID {order_id} not found")
            raise NotFoundError("Order", order_id)
        logger.info(f"Retrieved order with ID: {order_id}")
        return order
    
    async def get_by_user_id(self, db: AsyncSession, user_id: int):
        """Получить заказы пользователя"""
        logger.info(f"Retrieving orders for user ID: {user_id}")
        # Проверяем существование пользователя
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            logger.warning(f"User with ID {user_id} not found when retrieving orders")
            raise NotFoundError("User", user_id)
        
        orders = await order_crud.get_by_user_id(db, user_id)
        logger.info(f"Retrieved {len(orders)} orders for user ID: {user_id}")
        return orders
    
    async def create(self, db: AsyncSession, user_id: int, product_name: str, price):
        """Create a new order"""
        logger.info(f"Creating new order: user_id={user_id}, product_name={product_name}, price={price}")
        
        # Check user existence
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            logger.warning(f"Cannot create order: User with ID {user_id} not found")
            raise NotFoundError("User", user_id)
        
        # Price validation
        try:
            # Convert to Decimal for precision
            decimal_price = Decimal(str(price))
            
            # Validate positive price
            if decimal_price <= 0:
                logger.warning(f"Price validation failed: price {price} is not positive")
                raise ValidationError("Price must be greater than zero")
            
            # Limit to 2 decimal places
            decimal_price = decimal_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # Check if price has more than 10 significant digits
            if len(decimal_price.as_tuple().digits) > 10:
                logger.warning(f"Price validation failed: price {price} has too many digits")
                raise ValidationError("Price is too large, maximum 10 digits allowed")
                
        except InvalidOperation:
            logger.warning(f"Invalid price format: {price}")
            raise ValidationError(f"Invalid price format: {price}")
        
        # Product name validation
        if not product_name or not product_name.strip():
            logger.warning("Product name validation failed: empty name")
            raise ValidationError("Product name cannot be empty")
        
        if len(product_name) > 255:
            logger.warning(f"Product name validation failed: name length is {len(product_name)}")
            raise ValidationError("Product name is too long, maximum 255 characters allowed")
        
        try:
            order = await order_crud.create(
                db, 
                user_id=user_id, 
                product_name=product_name, 
                price=decimal_price
            )
            logger.info(f"Created new order with ID: {order.id}")
            log_business_event(
                logger, 
                "created", 
                "order", 
                order.id, 
                {"user_id": user_id, "product_name": product_name, "price": str(decimal_price)}
            )
            return order
        except IntegrityError as e:
            log_exception(
                logger, 
                e, 
                {"user_id": user_id, "product_name": product_name, "price": str(decimal_price)}
            )
            raise ValidationError(f"Database error: {str(e)}")
 
    async def delete(self, db: AsyncSession, order_id: int):
        """Удалить заказ"""
        logger.info(f"Deleting order with ID: {order_id}")
        # Проверяем существование заказа
        order = await order_crud.get_by_id(db, order_id)
        if not order:
            logger.warning(f"Cannot delete: Order with ID {order_id} not found")
            raise NotFoundError("Order", order_id)
        
        user_id = order.user_id
        product_name = order.product_name
        
        # Удаляем заказ
        await db.delete(order)
        await db.commit()
        logger.info(f"Order with ID {order_id} deleted successfully")
        log_business_event(
            logger, 
            "deleted", 
            "order", 
            order_id, 
            {"user_id": user_id, "product_name": product_name}
        )
        return True