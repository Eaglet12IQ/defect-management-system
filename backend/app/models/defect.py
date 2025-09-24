from datetime import datetime
from typing import Optional, List

from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Text, Enum as SAEnum, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship

from .base import Base

class DefectPriorityEnum(str, PyEnum):  # type: ignore[misc]
    LOW = "Низкий"
    MEDIUM = "Средний"
    HIGH = "Высокий"
    CRITICAL = "Критический"

class DefectStatusEnum(str, PyEnum):  # type: ignore[misc]
    NEW = "Новый"
    IN_PROGRESS = "В работе"
    UNDER_REVIEW = "На проверке"
    CLOSED = "Закрыт"
    CANCELED = "Отменен"

class Defect(Base):
    __tablename__ = "defects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    priority = Column(
        SAEnum(DefectPriorityEnum, name="defect_priority", native_enum=False),
        nullable=False
    )
    status = Column(
        SAEnum(DefectStatusEnum, name="defect_status", native_enum=False),
        nullable=False,
        default=DefectStatusEnum.NEW
    )
    assignee = Column(String(255), nullable=True)
    due_date = Column(DateTime, nullable=True)
    attachments = Column(JSON, nullable=True)  # List of file URLs or metadata

    # Creator linkage
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    creator = relationship("User", back_populates="created_defects")

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    project = relationship("Project", back_populates="defects")