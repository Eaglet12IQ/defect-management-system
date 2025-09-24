from fastapi import APIRouter, Depends, Response, Request, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_payload_from_refresh_token
from app.models.user import User
from app.models.profile import Profile
from app.models.project import Project
from pydantic import BaseModel

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    description: str
    manager_id: int
    status: str = "Планирование"

@router.get("/managers")
async def get_managers(response: Response, request: Request, db: Session = Depends(get_db)):
    payload = get_payload_from_refresh_token(request)
    role_id = payload.get("role")

    if role_id != 3:
        raise HTTPException(status_code=403, detail="Отказано в доступе!")

    managers = User.get_managers(db)

    result = []
    for manager in managers:
        profile = Profile.get_profile(db, manager.id)
        result.append({
            "id": manager.id,
            "username": manager.username,
            "first_name": profile.first_name if profile else "",
            "last_name": profile.last_name if profile else "",
            "role": manager.role_id
        })

    return result

@router.post("/create_project")
async def get_managers(project_data: ProjectCreate, response: Response, request: Request, db: Session = Depends(get_db)):
    payload = get_payload_from_refresh_token(request)
    role_id = payload.get("role")

    if role_id != 3:
        raise HTTPException(status_code=403, detail="Отказано в доступе!")
    
    manager = User.get_user(db, project_data.manager_id)
    if not manager:
        raise HTTPException(status_code=400, detail="Менеджер не найден!")

    Project.create_project(db, project_data.name, project_data.description, project_data.manager_id, project_data.status)

    return {
        "message": "Новый проект создан."
    }

@router.get("/projects")
async def get_projects(
    request: Request,
    db: Session = Depends(get_db)
):
    # Get user from token
    payload = get_payload_from_refresh_token(request)
    user_id = payload.get("sub")
    role_id = payload.get("role")

    # If user is manager (role 2), show only their projects
    if role_id == 2:
        projects = db.query(Project).filter(Project.manager_id == user_id).all()
    else:
        # For other roles, show all projects
        projects = db.query(Project).all()

    result = []
    for project in projects:
        result.append({
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "manager_id": project.manager_id,
            "manager_name": f"{project.manager.profile.first_name} {project.manager.profile.last_name}" if project.manager.profile else "Неизвестно",
            "status": project.status
        })

    return result
