from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

from enum import Enum as PyEnum
from sqlalchemy import Enum as SAEnum

class RoleEnum(str, PyEnum):
    ENGINEER = "Инженер"
    MANAGER = "Менеджер"
    LEADER = "Руководитель"
    SUPERADMIN = "Суперадмин"

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(
        SAEnum(RoleEnum, name="role_name", native_enum=False),
        nullable=False
    )

    # Связь "один ко многим" с пользователями
    users = relationship("User", back_populates="role")