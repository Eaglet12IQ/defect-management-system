from fastapi import APIRouter, Depends, Response, Request, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_payload_from_refresh_token
from app.models.user import User
from app.models.profile import Profile
from app.models.project import Project
from app.models.defect import Defect
from pydantic import BaseModel

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    description: str
    manager_id: int

class ProjectEdit(BaseModel):
    project_id: int
    name: str
    description: str
    status: str
    manager_id: int | None = None  # Optional for managers

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
async def create_project(project_data: ProjectCreate, response: Response, request: Request, db: Session = Depends(get_db)):
    payload = get_payload_from_refresh_token(request)
    role_id = payload.get("role")

    if role_id != 3:
        raise HTTPException(status_code=403, detail="Отказано в доступе!")
    
    manager = User.get_user(db, project_data.manager_id)
    if not manager:
        raise HTTPException(status_code=400, detail="Менеджер не найден!")

    Project.create_project(db, project_data.name, project_data.description, project_data.manager_id)

    return {
        "message": "Новый проект создан."
    }

@router.put("/edit_project")
async def edit_project(project_data: ProjectEdit, response: Response, request: Request, db: Session = Depends(get_db)):
    payload = get_payload_from_refresh_token(request)
    user_id = int(payload.get("sub"))
    role_id = payload.get("role")

    # Get the project to check permissions
    project = Project.get_project(db, project_data.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден!")

    # Check permissions
    if role_id == 3:  # Admin can edit any project
        pass
    elif role_id == 2:  # Manager can only edit their own projects
        if project.manager_id != user_id:
            raise HTTPException(status_code=403, detail="Отказано в доступе!")
        # Managers cannot change the manager_id field (if they try to provide one)
        if project_data.manager_id is not None and project_data.manager_id != project.manager_id:
            raise HTTPException(status_code=403, detail="Менеджеры не могут изменять прикрепленного менеджера!")
    else:
        raise HTTPException(status_code=403, detail="Отказано в доступе!")

    # For managers, use the existing manager_id, for admins use the provided one
    final_manager_id = project.manager_id if role_id == 2 else project_data.manager_id

    # Validate manager exists only for admins
    if role_id == 3:
        manager = User.get_user(db, final_manager_id)
        if not manager:
            raise HTTPException(status_code=400, detail="Менеджер не найден!")

    Project.edit_project(db, project_data.project_id, project_data.name, project_data.description, final_manager_id, project_data.status)

    return {
        "message": "Проект изменен."
    }

@router.get("/projects")
async def get_projects(
    request: Request,
    db: Session = Depends(get_db)
):
    # Get user from token
    payload = get_payload_from_refresh_token(request)
    user_id = int(payload.get("sub"))
    role_id = payload.get("role")

    # If user is manager (role 2), show only their projects
    if role_id == 2:
        projects = db.query(Project).filter(Project.manager_id == user_id).all()
    else:
        # For other roles, show all projects
        projects = db.query(Project).all()

    # Get defect counts for all projects
    from sqlalchemy import func
    defect_counts = db.query(
        Defect.project_id,
        func.count(Defect.id).label('defect_count')
    ).group_by(Defect.project_id).all()

    defect_count_dict = {count.project_id: count.defect_count for count in defect_counts}

    result = []
    for project in projects:
        defect_count = defect_count_dict.get(project.id, 0)
        result.append({
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "manager_id": project.manager_id,
            "manager_name": f"{project.manager.profile.first_name} {project.manager.profile.last_name}" if project.manager.profile else "Неизвестно",
            "status": project.status,
            "defect_count": defect_count
        })

    return result

@router.get("/projects/{project_id}")
async def get_project_by_id(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    # Get user from token
    payload = get_payload_from_refresh_token(request)
    user_id = int(payload.get("sub"))
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
