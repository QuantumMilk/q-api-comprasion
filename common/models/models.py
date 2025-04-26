from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, func
from sqlalchemy.orm import relationship
from common.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Отношение к заказам пользователя
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Отношение к пользователю
    user = relationship("User", back_populates="orders")