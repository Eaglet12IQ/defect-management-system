from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship, Session
from .base import Base
from enum import Enum as PyEnum
from sqlalchemy import Enum as SAEnum

class ProjectStatusEnum(str, PyEnum):
    PLANNING = "Планирование"
    ACTIVE = "Активный"
    COMPLETED = "Завершен"
    PAUSED = "Приостановлен"

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(
        SAEnum(ProjectStatusEnum, name="project_status", native_enum=False),
        nullable=False,
        default=ProjectStatusEnum.PLANNING
    )
    manager = relationship("User", back_populates="managed_projects")

    # Связь "один ко многим" с дефектами
    defects = relationship("Defect", back_populates="project")
    reports = relationship("Report", back_populates="project")

    def create_project(db: Session, name, description, manager_id, status=ProjectStatusEnum.PLANNING):
        db_project = Project(name=name, description=description, manager_id=manager_id, status=status)
        db.add(db_project)
        db.commit()
        db.refresh(db_project)

        return db_project
