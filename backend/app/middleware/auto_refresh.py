from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.core.security import (
    SECRET_KEY,
    ALGORITHM,
    create_access_token,
    verify_refresh_token,
)
import re

EXCLUDED_PATHS = [
    "/api/auth/", 
    "/api/profiles/",  # Исключает все пути, начинающиеся с /api/profiles/
    "/static/",
    "/docs", 
    "/openapi.json", 
    "/redoc",
    "/api/collections",
    "/api/stamps"
]

async def auto_refresh_token_middleware(request: Request, call_next):
    # Проверяем, является ли путь /api/profiles/{user_id}/settings
    is_user_settings_path = re.match(
        r'^/api/profiles/\d+/user_settings$',  # \d+ — только цифры для user_id
        request.url.path
    ) is not None

    is_collections_delete_path = re.match(
        r'^/api/collections/delete/\d+$',  # \d+ — только цифры для user_id
        request.url.path
    ) is not None

    is_collections_update_path = re.match(
        r'^/api/collections/update/\d+$',  # \d+ — только цифры для user_id
        request.url.path
    ) is not None

    is_stamps_update_path = re.match(
        r'^/api/stamps/update/\d+$',  # \d+ — только цифры для user_id
        request.url.path
    ) is not None

    is_stamps_delete_path = re.match(
        r'^/api/stamps/delete/\d+$',  # \d+ — только цифры для user_id
        request.url.path
    ) is not None

    is_users_update_path = re.match(
        r'^/api/profiles/users/\d+$',  # \d+ — только цифры для user_id
        request.url.path
    ) is not None

    is_profiles_update_path = re.match(
        r'^/api/profiles/collectors/\d+$',  # \d+ — только цифры для user_id
        request.url.path
    ) is not None

    is_collections_create_path = re.match(
        r'^/api/collections/create$',  # \d+ — только цифры для user_id
        request.url.path
    ) is not None

    is_stamps_create_path = re.match(
        r'^/api/stamps/create$',  # \d+ — только цифры для user_id
        request.url.path
    ) is not None

    is_collector_settings_path = re.match(
        r'^/api/profiles/\d+/collector_settings$',  # \d+ — только цифры для user_id
        request.url.path
    ) is not None

    is_change_avatar_path = re.match(
        r'^/api/profiles/\d+/change_avatar$',  # \d+ — только цифры для user_id
        request.url.path
    ) is not None

    is_logout_path = re.match(
        r'^/api/auth/logout$',  # \d+ — только цифры для user_id
        request.url.path
    ) is not None

    is_delete_path = re.match(
        r'^/api/auth/delete$',  # \d+ — только цифры для user_id
        request.url.path
    ) is not None

    # Если путь исключен И НЕ является /api/profiles/{user_id}/settings
    if any(request.url.path.startswith(p) for p in EXCLUDED_PATHS) and not is_user_settings_path and not is_stamps_update_path and not is_profiles_update_path and not is_users_update_path and not is_collections_update_path and not is_stamps_delete_path and not is_collections_delete_path and not is_stamps_create_path and not is_collections_create_path and not is_change_avatar_path and not is_collector_settings_path and not is_logout_path and not is_delete_path:
        return await call_next(request)
    
    # Остальная логика middleware...
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Требуется аутентификация"},
        )
    
    access_token = auth_header.split(" ")[1]
    db: Session = next(get_db())

    try:
        payload = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        exp = payload.get("exp")
        if not exp:
            return JSONResponse(
                status_code=401,
                content={"detail": "Токен не содержит времени истечения"},
            )
        
        return await call_next(request)

    except ExpiredSignatureError:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token отсутствует")

        new_access_token = await refresh_access_token(refresh_token, db)
        request.state.token = f"Bearer {new_access_token}"
        response = await call_next(request)
        response.headers["New-Access-Token"] = new_access_token
        return response
    except JWTError:
        return JSONResponse(
            status_code=401,
            content={"detail": "Недействительный токен"},
        )

async def refresh_access_token(refresh_token: str, db: Session):
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Недействительный refresh token")
    
    id = payload.get("sub")
    user = db.query(User).filter(User.id == int(id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    
    new_access_token = create_access_token(data={"sub": str(user.id)})
    return new_access_token