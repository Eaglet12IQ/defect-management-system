from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Session
from .base import Base
from app.models.collection import Collection # for model
from fastapi import HTTPException

class Collector(Base):
    __tablename__ = "collectors"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    avatar_url = Column(String, nullable=False, default="/static/avatars/default_avatar.png")
    country = Column(String(50), nullable=True)
    phone_number = Column(String(20), nullable=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    middle_name = Column(String(50), nullable=True)  # Отчество может быть пустым

    # Связи
    user = relationship("User", back_populates="collector")
    collections = relationship("Collection", back_populates="collector", cascade="all, delete-orphan")  # Один-ко-многим

    def get_collector(db: Session, user_id):
        collector = db.query(Collector).filter(Collector.user_id == user_id).first()
        if not collector:
            raise HTTPException(status_code=400, detail="Коллекционер не найден с таким ID!")
        
        return collector
