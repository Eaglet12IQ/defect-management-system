from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Stamp(Base):
    __tablename__ = "stamps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    serial_number = Column(String(50), nullable=False, unique=True)  # Уникальный серийный номер
    country = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)  # Исправлено: Integer без аргумента
    circulation = Column(Integer, nullable=False)
    cost = Column(Integer, nullable=False)
    perforation = Column(Integer, nullable=False)
    topic = Column(String(100), nullable=False)
    features = Column(String(500), nullable=True)
    photo_url = Column(String, nullable=False, default="/static/avatars/default_avatar.png")
    
    # Связь один-к-одному с Collection
    collection_id = Column(Integer, ForeignKey("collections.id"))
    collection = relationship("Collection", back_populates="stamps")