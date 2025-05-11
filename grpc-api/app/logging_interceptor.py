import time
import uuid
import grpc
from grpc.aio import ServerInterceptor
from common.utils.logging import get_logger, log_business_event

logger = get_logger("grpc_interceptor", "grpc_requests.log")

class LoggingInterceptor(ServerInterceptor):
    """gRPC сервисный интерцептор для логирования запросов."""
    
    async def intercept_service(self, continuation, handler_call_details):
        """Логирует gRPC запросы и ответы."""
        method = handler_call_details.method
        # Генерируем уникальный идентификатор запроса
        request_id = str(uuid.uuid4())
        
        # Получаем метаданные из запроса
        metadata = dict(handler_call_details.invocation_metadata)
        
        # Логируем начало запроса
        logger.info(
            f"Incoming gRPC request: {method}",
            context={
                "request_id": request_id,
                "method": method,
                "metadata": metadata
            }
        )
        
        # Фиксируем время начала обработки
        start_time = time.time()
        
        # Вызываем следующий обработчик в цепочке
        handler = await continuation(handler_call_details)
        
        # Создаем обёртку для метода
        if handler:
            original_func = handler.unary_unary
            
            # Обертка для unary-unary методов
            async def logging_wrapper(request, context):
                try:
                    # Добавляем request_id в контекст
                    context.set_trailing_metadata((
                        ('x-request-id', request_id),
                    ))
                    
                    # Логируем данные запроса
                    logger.debug(
                        f"gRPC request data for {method}",
                        context={
                            "request_id": request_id,
                            "request": str(request)
                        }
                    )
                    
                    # Выполняем оригинальный вызов
                    response = await original_func(request, context)
                    
                    # Вычисляем время выполнения
                    execution_time = (time.time() - start_time) * 1000
                    
                    # Логируем успешный ответ
                    logger.info(
                        f"gRPC response for {method} completed successfully",
                        context={
                            "request_id": request_id,
                            "method": method,
                            "execution_time_ms": execution_time,
                            "status_code": grpc.StatusCode.OK.value[0]
                        }
                    )
                    
                    # Логируем данные ответа
                    logger.debug(
                        f"gRPC response data for {method}",
                        context={
                            "request_id": request_id,
                            "response": str(response)
                        }
                    )
                    
                    return response
                except Exception as e:
                    # Вычисляем время до возникновения исключения
                    execution_time = (time.time() - start_time) * 1000
                    
                    # Логируем ошибку
                    logger.error(
                        f"Error processing gRPC request {method}",
                        exc_info=e,
                        context={
                            "request_id": request_id,
                            "method": method,
                            "execution_time_ms": execution_time
                        }
                    )
                    
                    # Пробрасываем исключение дальше
                    raise
            
            # Заменяем метод на обертку
            handler.unary_unary = logging_wrapper
        
        return handler