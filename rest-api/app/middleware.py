import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from common.utils.logging import get_logger, log_request

logger = get_logger("rest_middleware", "rest_requests.log")

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP запросов."""
    
    async def dispatch(self, request: Request, call_next):
        # Генерируем уникальный идентификатор запроса
        request_id = str(uuid.uuid4())
        
        # Добавляем request_id в заголовки
        request.state.request_id = request_id
        
        # Записываем начало запроса
        start_time = time.time()
        
        # Пытаемся получить тело запроса (если оно есть)
        body = await self._get_request_body(request)
        
        # Логируем входящий запрос
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            context={
                "request_id": request_id,
                "http_method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client": request.client.host if request.client else "unknown",
                "body": body if body else None
            }
        )
        
        try:
            # Передаем запрос дальше
            response = await call_next(request)
            
            # Вычисляем время выполнения
            execution_time = (time.time() - start_time) * 1000
            
            # Логируем информацию о запросе
            log_request(
                logger,
                request_id,
                request.method,
                request.url.path,
                response.status_code,
                execution_time
            )
            
            # Добавляем request_id в заголовки ответа
            response.headers["X-Request-ID"] = request_id
            
            return response
        except Exception as exc:
            # Вычисляем время до возникновения исключения
            execution_time = (time.time() - start_time) * 1000
            
            # Логируем ошибку
            logger.error(
                f"Error processing request: {request.method} {request.url.path}",
                exc_info=exc,
                context={
                    "request_id": request_id,
                    "http_method": request.method,
                    "path": request.url.path,
                    "execution_time_ms": execution_time
                }
            )
            
            # Пробрасываем исключение дальше
            raise
    
    async def _get_request_body(self, request: Request):
        """Пытается получить тело запроса."""
        try:
            body = await request.body()
            # Сохраняем тело запроса для повторного использования
            await request.body()
            return body.decode()
        except Exception:
            return None