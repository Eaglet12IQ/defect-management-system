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

class ProjectEdit(ProjectCreate):
    project_id: int

@router.get("/projects")
async def get_projects(response: Response, request: Request, db: Session = Depends(get_db)):
    payload = get_payload_from_refresh_token(request)
    role_id = payload.get("role")

    if role_id != 1:
        raise HTTPException(status_code=403, detail="Отказано в доступе!")

    projects = Project.get_project(db, None)

    result = []
    for project in projects:
        result.append({
            "id": project.id,
            "name": project.name,
        })

    return result

@router.post("/create_defect")
async def create_defect(project_data: ProjectCreate, response: Response, request: Request, db: Session = Depends(get_db)):
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

@router.put("/edit_defect")
async def edit_defect(project_data: ProjectEdit, response: Response, request: Request, db: Session = Depends(get_db)):
    payload = get_payload_from_refresh_token(request)
    role_id = payload.get("role")

    if role_id != 3:
        raise HTTPException(status_code=403, detail="Отказано в доступе!")
    
    manager = User.get_user(db, project_data.manager_id)
    if not manager:
        raise HTTPException(status_code=400, detail="Менеджер не найден!")

    Project.edit_project(db, project_data.project_id, project_data.name, project_data.description, project_data.manager_id, project_data.status)

    return {
        "message": "Проект изменен."
    }

@router.get("/defects")
async def get_defects(
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

@router.get("/defects/{defect_id}")
async def get_defect_by_id(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    # Get user from token
    payload = get_payload_from_refresh_token(request)
    user_id = payload.get("sub")
    role_id = payload.get("role")

    # Get the project
    project = Project.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден!")

    # Check permissions - managers can only see their own projects
    if role_id == 2 and project.manager_id != user_id:
        raise HTTPException(status_code=403, detail="Отказано в доступе!")

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "manager_id": project.manager_id,
        "manager_name": f"{project.manager.profile.first_name} {project.manager.profile.last_name}" if project.manager.profile else "Неизвестно",
        "status": project.status
    }
