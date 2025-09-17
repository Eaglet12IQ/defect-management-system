from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Session
from .base import Base
from fastapi import HTTPException

class Profile(Base):
    __tablename__ = "profiles"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    avatar_url = Column(String, nullable=False, default="/static/avatars/default_avatar.png")
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    middle_name = Column(String(50), nullable=True)  # Отчество может быть пустым
    
    # Связи
    user = relationship("User", back_populates="profile")

    def get_profile(db: Session, user_id):
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()

        if not profile:
            raise HTTPException(status_code=400, detail="Профиль не найден с таким ID!")

        return profile