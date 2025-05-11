import os
import json
import logging
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, Optional

# Константы для уровней логирования
LOG_LEVEL_ENV = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}
LOG_LEVEL = LOG_LEVELS.get(LOG_LEVEL_ENV, logging.INFO)

# Форматтеры для разных типов вывода
CONSOLE_FORMAT = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
JSON_FORMAT = "%(message)s"

# Директория для логов
LOG_DIR = os.getenv("LOG_DIR", "/app/logs")
os.makedirs(LOG_DIR, exist_ok=True)


class JsonFormatter(logging.Formatter):
    """Форматтер для вывода логов в JSON формате."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
            "message": record.getMessage(),
        }
        
        # Добавляем дополнительные поля, если они есть
        if hasattr(record, "extra") and record.extra:
            log_data.update(record.extra)
        
        # Добавляем информацию об исключении, если оно есть
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_data)


class ContextLogger(logging.Logger):
    """Расширенный логгер с поддержкой контекста."""
    
    def _log_with_context(self, level, msg, args, exc_info=None, extra=None, stack_info=False, context=None):
        """Логирование с добавлением контекста."""
        if context:
            if not extra:
                extra = {}
            extra["extra"] = context
        
        return super().log(level, msg, args, exc_info, extra, stack_info)
    
    def debug(self, msg, *args, **kwargs):
        context = kwargs.pop("context", None)
        self._log_with_context(logging.DEBUG, msg, args, context=context, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        context = kwargs.pop("context", None)
        self._log_with_context(logging.INFO, msg, args, context=context, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        context = kwargs.pop("context", None)
        self._log_with_context(logging.WARNING, msg, args, context=context, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        context = kwargs.pop("context", None)
        self._log_with_context(logging.ERROR, msg, args, context=context, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        context = kwargs.pop("context", None)
        self._log_with_context(logging.CRITICAL, msg, args, context=context, **kwargs)


def get_logger(name: str, log_file: Optional[str] = None, json_format: bool = True) -> ContextLogger:
    """
    Создает и настраивает логгер.
    
    Args:
        name: Имя логгера
        log_file: Путь к файлу логов, если None - используется только консольный вывод
        json_format: Если True, логи будут в JSON формате
    
    Returns:
        Настроенный логгер
    """
    # Регистрируем наш класс логгера
    logging.setLoggerClass(ContextLogger)
    
    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Очищаем обработчики, если они уже были добавлены
    if logger.handlers:
        logger.handlers.clear()
    
    # Добавляем консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    
    if json_format:
        console_formatter = JsonFormatter()
    else:
        console_formatter = logging.Formatter(CONSOLE_FORMAT)
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Добавляем файловый обработчик, если указан файл
    if log_file:
        file_path = os.path.join(LOG_DIR, log_file)
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(LOG_LEVEL)
        
        if json_format:
            file_formatter = JsonFormatter()
        else:
            file_formatter = logging.Formatter(CONSOLE_FORMAT)
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Стандартные обработчики событий
def log_request(logger, request_id, method, path, status_code, execution_time):
    """Логирует информацию о HTTP запросе."""
    logger.info(
        f"HTTP {method} {path} completed with status {status_code} in {execution_time:.2f}ms",
        context={
            "request_id": request_id,
            "http_method": method,
            "path": path,
            "status_code": status_code,
            "execution_time_ms": execution_time
        }
    )


def log_database_query(logger, query, params, execution_time):
    """Логирует информацию о запросе к базе данных."""
    logger.debug(
        f"Database query executed in {execution_time:.2f}ms",
        context={
            "query": query,
            "params": params,
            "execution_time_ms": execution_time
        }
    )


def log_exception(logger, exc, context=None):
    """Логирует информацию об исключении."""
    if context is None:
        context = {}
    
    logger.error(
        f"Exception occurred: {str(exc)}",
        exc_info=exc,
        context=context
    )


def log_business_event(logger, event_type, entity_type, entity_id=None, details=None):
    """Логирует бизнес-событие."""
    context = {
        "event_type": event_type,
        "entity_type": entity_type,
    }
    
    if entity_id is not None:
        context["entity_id"] = entity_id
    
    if details:
        context["details"] = details
    
    logger.info(f"Business event: {event_type} {entity_type}", context=context)