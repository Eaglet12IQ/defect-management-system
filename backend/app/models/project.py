from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    manager = relationship("User", back_populates="managed_projects")

    # Связь "один ко многим" с дефектами
    defects = relationship("Defect", back_populates="project")
    reports = relationship("Report", back_populates="project")