from sqlalchemy import Column, Integer, String, ForeignKey
from fastapi import HTTPException, Response, Request
from sqlalchemy.orm import relationship, Session
from .base import Base
from app.models.role import Role # for model
from app.models.collector import Collector
import os
from app.core.security import get_payload_from_refresh_token
from app.schemas.user import UserLoginWithPasswordValidation, UserCreateWithPasswordValidation
from app.core.security import verify_password, create_access_token, create_refresh_token, REFRESH_TOKEN_EXPIRE_DAYS, get_password_hash

DEFAULT_AVATAR = "/static/avatars/default_avatar.png"  # путь по умолчанию
AVATAR_FOLDER = os.path.join("static", "avatars")  # путь к папке с аватарками

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)  # Новое поле
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, default=2)
    
    # Связь "многие к одному" с ролями
    role = relationship("Role", back_populates="users")
    collector = relationship("Collector", back_populates="user", uselist=False, cascade="all, delete")  # <-- Add this)

    def delete(db: Session, response: Response, request: Request):
        payload = get_payload_from_refresh_token(request)
        access_user_id = payload.get("sub")
        user = User.get_user(db, access_user_id)
        collector = Collector.get_collector(db, access_user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Пользователь не найден с таким ID!")
        
        if collector.avatar_url and collector.avatar_url != DEFAULT_AVATAR:
            avatar_filename = os.path.basename(collector.avatar_url)  # извлекаем имя файла
            avatar_path = os.path.join(AVATAR_FOLDER, avatar_filename)
            if os.path.exists(avatar_path):
                try:
                    os.remove(avatar_path)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Ошибка при удалении аватарки: {str(e)}")
        
        response.delete_cookie(
            key="refresh_token",
            secure=False,  # Обязательно, если кука устанавливалась с secure=True
            httponly=True,  # Если использовалось при установке
            samesite="lax",  
        )

        db.delete(user)
        db.commit()

        return {
            "message": "Пользователь удален.",
        }
    
    def login(db: Session, response: Response, user: UserLoginWithPasswordValidation):
        user_bd = db.query(User).filter((User.email == user.username) | (User.username == user.username)).first()

        if not user_bd:
            raise HTTPException(status_code=400, detail="Пользователь не найден!")
        
        if not verify_password(user.password, user_bd.hashed_password):
            raise HTTPException(status_code=400, detail="Пароль введен неверно!")
        
        access_token = create_access_token(data={
            "sub": str(user_bd.id),
            "role": user_bd.role_id,  # или user_bd.role_id, если имя не доступно
            "username": user_bd.username
        })
        refresh_token = create_refresh_token(data={
            "sub": str(user_bd.id),
            "role": user_bd.role_id
        })

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  
            samesite="lax",  
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        )

        return {
            "message": "Пользователь авторизован.",
            "access_token": access_token,
            "token_type": "bearer",
            "username": user_bd.username,
            "email": user_bd.email
        }
    
    def logout(db: Session, request: Request, response: Response):
        payload = get_payload_from_refresh_token(request)
        access_user_id = payload.get("sub")
        
        user = db.query(User).filter(User.id == int(access_user_id)).first()
        if not user:
            raise HTTPException(status_code=401, detail="Пользователь не найден с таким ID!")
        
        response.delete_cookie(
            key="refresh_token",
            httponly=True,  # Если использовалось при установке 
            samesite="lax",  
            secure=False,  # Обязательно, если кука устанавливалась с secure=True
        )

        return {
            "message": "Пользователь вышел из системы.",
        }
    
    def register(db: Session, response: Response, user: UserCreateWithPasswordValidation):
        if user.password != user.re_password:
            raise HTTPException(status_code=400, detail="Пароли не совпадают!")
        db_user_email = db.query(User).filter(User.email == user.email).first()
        db_user_username = db.query(User).filter(User.username == user.username).first()
        if db_user_email or db_user_username:
            raise HTTPException(status_code=400, detail="Почта или логин уже зарезервированы!")
        
        # Хэширование пароля
        hashed_password = get_password_hash(user.password)
        
        # Создание нового пользователя
        db_user = User(email=user.email, username=user.username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db_collector = Collector(user_id=db_user.id)
        db.add(db_collector)
        db.commit()

            # Генерируем токены для нового пользователя
        access_token = create_access_token(data={
            "sub": str(db_user.id),
            "role": db_user.role_id,  # или user_bd.role_id, если имя не доступно
            "username": db_user.username
        })
        refresh_token = create_refresh_token(data={
            "sub": str(db_user.id),
            "role": db_user.role_id
        })
        
        # Устанавливаем refresh token в куки
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",  
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        )
        
        return {
            "message": "Пользователь зарегистрирован и авторизован.",
            "access_token": access_token,
            "token_type": "bearer",
            "username": db_user.username,
            "email": db_user.email,
            "id": db_user.id,
        }
    
    def get_user(db: Session, user_id):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="Пользователь не найден с таким ID!")
        
        return user