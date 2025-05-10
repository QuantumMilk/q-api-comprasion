from typing import Dict, Any, Type, TypeVar, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import DeclarativeBase

T = TypeVar('T', bound=DeclarativeBase)

def model_to_dict(model: T) -> Dict[str, Any]:
    """Convert SQLAlchemy model to dictionary"""
    if model is None:
        return {}
    
    result = {}
    for column in model.__table__.columns:
        value = getattr(model, column.name)
        result[column.name] = value
    
    return result