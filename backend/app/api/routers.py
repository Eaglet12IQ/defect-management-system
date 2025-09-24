from fastapi import APIRouter
from app.api.endpoints import dashboard
from app.api.endpoints import auth
from app.api.endpoints import project
from app.api.endpoints import defect

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(project.router, tags=["project"]) 
api_router.include_router(defect.router, tags=["defect"]) 