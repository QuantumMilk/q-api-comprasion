class ServiceError(Exception):
    """Базовый класс для всех исключений сервисного слоя"""
    pass

class NotFoundError(ServiceError):
    """Исключение выбрасывается, когда объект не найден"""
    def __init__(self, entity_type, entity_id=None, message=None):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.message = message or f"{entity_type} with ID {entity_id} not found"
        super().__init__(self.message)

class ValidationError(ServiceError):
    """Исключение выбрасывается при ошибке валидации"""
    pass

class AlreadyExistsError(ServiceError):
    """Исключение выбрасывается, когда объект уже существует"""
    def __init__(self, entity_type, field, value):
        self.entity_type = entity_type
        self.field = field
        self.value = value
        self.message = f"{entity_type} with {field}='{value}' already exists"
        super().__init__(self.message)