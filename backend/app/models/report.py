from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum as PyEnum
from sqlalchemy import Column, BigInteger, String, Enum as SAEnum, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.sql import func

class Report(Base):
    __tablename__ = "reports"

    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    project_id = Column(BigInteger, ForeignKey("projects.id"), nullable=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    file_path = Column(String(500), nullable=True)  # Path to CSV/Excel file
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="reports", foreign_keys=[user_id])
    project = relationship("Project", back_populates="reports")