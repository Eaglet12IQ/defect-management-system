from sqlalchemy import Column, Integer, String, ForeignKey
from fastapi import HTTPException, Response, Request, status
from sqlalchemy.orm import relationship, Session
from .base import Base
from app.models.role import Role # for model
from app.models.profile import Profile
from .defect import Defect
from .project import Project
from .auditlog import AuditLog
from .report import Report
import os
from fastapi.responses import JSONResponse
import shutil
import uuid
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
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete")  # <-- Add this)

    created_defects = relationship("Defect", back_populates="creator", foreign_keys="Defect.creator_id")
    managed_projects = relationship("Project", back_populates="manager")

    audit_logs = relationship("AuditLog", back_populates="user")
    reports = relationship("Report", back_populates="user", foreign_keys="Report.user_id")

    def delete(db: Session, response: Response, request: Request):
        payload = get_payload_from_refresh_token(request)
        access_user_id = payload.get("sub")
        user = User.get_user(db, access_user_id)
        profile = Profile.get_profile(db, access_user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Пользователь не найден с таким ID!")

        if profile.avatar_url and profile.avatar_url != DEFAULT_AVATAR:
            avatar_filename = os.path.basename(profile.avatar_url)  # извлекаем имя файла
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
        
        # Получить профиль для аватарки
        profile = Profile.get_profile(db, user_bd.id)
        avatar_url = profile.avatar_url if profile else DEFAULT_AVATAR

        access_token = create_access_token(data={
            "sub": str(user_bd.id),
            "role": user_bd.role_id,  # или user_bd.role_id, если имя не доступно
            "username": user_bd.username,
            "avatar": "http://localhost:8000" + avatar_url
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
            "token_type": "bearer"
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

    def register(db, response, username, email, password, re_password, first_name, last_name, middle_name, role, avatar):
        # Validate required fields
        if not first_name or not last_name:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "Имя и фамилия обязательны для заполнения!"})

        # Validate passwords match
        if password != re_password:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "Пароли не совпадают!"})

        # Check if email or username already exists
        if db.query(User).filter(User.email == email).first() or db.query(User).filter(User.username == username).first():
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "Почта или логин уже зарезервированы!"})

        # Hash password
        hashed_password = get_password_hash(password)

        # Create new user
        db_user = User(email=email, username=username, hashed_password=hashed_password, role_id=role)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Handle avatar upload
        avatar_url = "/static/avatars/default_avatar.png"
        if avatar:
            filename = f"{uuid.uuid4().hex}_{avatar.filename}"
            avatar_path = os.path.join("static", "avatars", filename)
            with open(avatar_path, "wb") as buffer:
                shutil.copyfileobj(avatar.file, buffer)
            avatar_url = f"/static/avatars/{filename}"

        # Create profile with avatar and names
        db_profile = Profile(
            user_id=db_user.id,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            avatar_url=avatar_url
        )
        db.add(db_profile)
        db.commit()

        return {
            "message": "Пользователь зарегистрирован и авторизован."
        }

    def get_user(db: Session, user_id):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="Пользователь не найден с таким ID!")
        return user
    
    def get_managers(db: Session):
        managers = db.query(User).filter(User.role_id == 2)
        if not managers:
            raise HTTPException(status_code=400, detail="Менеджеров не обнаружено в системе!")
        return managers
