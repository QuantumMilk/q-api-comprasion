import time
import uuid
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from common.utils.logging import get_logger, log_request

logger = get_logger("graphql_middleware", "graphql_requests.log")

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP и GraphQL запросов."""
    
    async def dispatch(self, request: Request, call_next):
        # Генерируем уникальный идентификатор запроса
        request_id = str(uuid.uuid4())
        
        # Добавляем request_id в заголовки
        request.state.request_id = request_id
        
        # Записываем начало запроса
        start_time = time.time()
        
        # Пытаемся получить тело запроса (особенно важно для GraphQL)
        body = await self._get_request_body(request)
        
        # Определяем, является ли запрос GraphQL запросом
        is_graphql = request.url.path.endswith("/graphql") and request.method == "POST"
        
        # Если это GraphQL запрос, логируем его особым образом
        if is_graphql and body:
            try:
                parsed_body = json.loads(body)
                query = parsed_body.get("query", "")
                variables = parsed_body.get("variables", {})
                operation_name = parsed_body.get("operationName")
                
                # Логируем GraphQL запрос
                logger.info(
                    f"Incoming GraphQL request: {operation_name or 'unnamed'}",
                    context={
                        "request_id": request_id,
                        "operation_name": operation_name,
                        "query": query,
                        "variables": variables,
                        "client": request.client.host if request.client else "unknown"
                    }
                )
            except json.JSONDecodeError:
                # Если не удалось разобрать JSON, логируем как обычный запрос
                logger.info(
                    f"Incoming request: {request.method} {request.url.path}",
                    context={
                        "request_id": request_id,
                        "http_method": request.method,
                        "path": request.url.path,
                        "body": body,
                        "client": request.client.host if request.client else "unknown"
                    }
                )
        else:
            # Логируем обычный HTTP запрос
            logger.info(
                f"Incoming request: {request.method} {request.url.path}",
                context={
                    "request_id": request_id,
                    "http_method": request.method,
                    "path": request.url.path,
                    "query_params": str(request.query_params),
                    "body": body if body else None,
                    "client": request.client.host if request.client else "unknown"
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
            
            # Если это GraphQL запрос, пытаемся логировать ответ
            if is_graphql and response.status_code == 200:
                response_body = await self._get_response_body(response)
                if response_body:
                    try:
                        response_data = json.loads(response_body)
                        errors = response_data.get("errors", [])
                        if errors:
                            logger.warning(
                                f"GraphQL response contains errors",
                                context={
                                    "request_id": request_id,
                                    "errors": errors
                                }
                            )
                    except json.JSONDecodeError:
                        pass
            
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
    
    async def _get_response_body(self, response):
        """Пытается получить тело ответа."""
        try:
            # Это может не работать с некоторыми типами ответов
            body = b""
            if hasattr(response, "body"):
                body = response.body
            return body.decode()
        except Exception:
            return None