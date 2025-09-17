from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base  # Предполагаем, что Base импортируется из вашего базового модуля

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(255), nullable=False, index=True)
    record_id = Column(Integer, nullable=False, index=True)
    action = Column(String(20), nullable=False)  # 'INSERT', 'UPDATE', 'DELETE'
    old_data = Column(JSON, nullable=True)  # Предыдущие значения
    new_data = Column(JSON, nullable=True)  # Новые значения
    changed_fields = Column(JSON, nullable=True)  # Изменённые поля (только для UPDATE)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    comment = Column(Text, nullable=True)  # Комментарий к изменению
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Связь с пользователем (опционально)
    user = relationship("User", back_populates="audit_logs")