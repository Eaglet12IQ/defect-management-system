from fastapi import APIRouter
from app.api.endpoints.auth import register, login, logout, delete
from app.api.endpoints.profile import profiles
from app.api.endpoints.setting import settings, change_avatar
from app.api.endpoints.collection import collections
from app.api.endpoints import stamps
from app.api.endpoints import admin

api_router = APIRouter()

api_router.include_router(register.router, prefix="/auth", tags=["auth"])
api_router.include_router(login.router, prefix="/auth", tags=["auth"])
api_router.include_router(logout.router, prefix="/auth", tags=["auth"])
api_router.include_router(delete.router, prefix="/auth", tags=["auth"])

api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(change_avatar.router, prefix="/settings", tags=["settings"])

api_router.include_router(collections.router, prefix="/collections", tags=["collections"])

api_router.include_router(stamps.router, prefix="/stamps", tags=["stamps"])

api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
