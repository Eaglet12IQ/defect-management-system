from fastapi import APIRouter, Depends, Response, Request, Form, File, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_payload_from_refresh_token
from app.models.user import User
from app.models.profile import Profile
from app.models.project import Project
from app.models.defect import Defect, DefectPriorityEnum, DefectStatusEnum
from pydantic import BaseModel
from fastapi.datastructures import UploadFile as UploadFileType
from typing import Optional, List
from datetime import datetime
import os
import shutil
from pathlib import Path

router = APIRouter()

class DefectCreate(BaseModel):
    title: str
    description: str
    priority: DefectPriorityEnum
    project_id: int
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None

@router.get("/projects_for_defect")
async def get_projects(response: Response, request: Request, db: Session = Depends(get_db)):
    payload = get_payload_from_refresh_token(request)
    role_id = payload.get("role")

    # Allow users with role 1 (defect creators) to see projects
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
async def create_defect(
    response: Response,
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    priority: str = Form(...),
    project_id: int = Form(...),
    assignee: str = Form(None),
    due_date: str = Form(None),
    attachments: List[UploadFileType] = File(None),
    db: Session = Depends(get_db)
):
    payload = get_payload_from_refresh_token(request)
    user_id = int(payload.get("sub"))
    role_id = payload.get("role")

    # Only allow users with role 1 (defect creators) to create defects
    if role_id != 1:
        raise HTTPException(status_code=403, detail="Отказано в доступе!")

    # Validate project exists
    project = Project.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден!")

    # Validate priority
    try:
        priority_enum = DefectPriorityEnum(priority)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный приоритет дефекта!")

    # Parse due date if provided
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат даты!")

    # Create the defect first to get the ID
    new_defect = Defect(
        title=title,
        description=description,
        priority=priority_enum,
        status=DefectStatusEnum.NEW,
        assignee=assignee,
        due_date=parsed_due_date,
        attachments=None,
        creator_id=user_id,
        project_id=project_id
    )

    db.add(new_defect)
    db.commit()
    db.refresh(new_defect)

    # Create folder structure: static/defects/{defect_id}/
    base_static_path = Path("static/defects")
    defect_folder = base_static_path / str(new_defect.id)
    defect_folder.mkdir(parents=True, exist_ok=True)

    # Handle file attachments
    attachments_data = []
    if attachments:
        for attachment in attachments:
            if attachment and attachment.filename:
                # Generate unique filename to avoid conflicts
                file_extension = Path(attachment.filename).suffix
                timestamp = int(datetime.now().timestamp())
                unique_filename = f"{timestamp}_{attachment.filename}"
                file_path = defect_folder / unique_filename

                # Save file to disk
                try:
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(attachment.file, buffer)

                    # Store only the file path
                    attachments_data.append(f"static/defects/{new_defect.id}/{unique_filename}")
                except Exception as e:
                    print(f"Error saving file {attachment.filename}: {e}")
                    continue

    # Update defect with attachments data
    new_defect.attachments = attachments_data
    db.commit()

    return {
        "message": "Дефект успешно создан!",
        "defect_id": new_defect.id
    }

@router.put("/edit_defect")
async def edit_defect(project_data, response: Response, request: Request, db: Session = Depends(get_db)):
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

    # Get defects based on user role
    if role_id == 1:  # Engineers - show only their created defects
        defects = db.query(Defect).filter(Defect.creator_id == user_id).all()
    elif role_id == 2:  # Managers - show defects for their projects
        # Get projects managed by this user
        managed_projects = db.query(Project).filter(Project.manager_id == user_id).all()
        project_ids = [project.id for project in managed_projects]
        defects = db.query(Defect).filter(Defect.project_id.in_(project_ids)).all()
    else:  # Other roles (admin, etc.) - show all defects
        defects = db.query(Defect).all()

    result = []
    for defect in defects:
        # Get project info
        project = db.query(Project).filter(Project.id == defect.project_id).first()
        creator = db.query(User).filter(User.id == defect.creator_id).first()

        result.append({
            "id": defect.id,
            "title": defect.title,
            "description": defect.description,
            "status": defect.status.value,
            "priority": defect.priority.value,
            "assignee": defect.assignee,
            "due_date": defect.due_date.isoformat() if defect.due_date else None,
            "attachments": defect.attachments or [],
            "project_id": defect.project_id,
            "project_name": project.name if project else "Неизвестно",
            "creator_id": defect.creator_id,
            "creator_name": f"{creator.profile.first_name} {creator.profile.last_name}" if creator and creator.profile else "Неизвестно"
        })

    return result

@router.get("/defects/{defect_id}")
async def get_defect_by_id(
    defect_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    # Get user from token
    payload = get_payload_from_refresh_token(request)
    user_id = int(payload.get("sub"))
    role_id = payload.get("role")

    # Get the defect
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=404, detail="Дефект не найден!")

    # Check permissions
    if role_id == 1 and defect.creator_id != user_id:
        raise HTTPException(status_code=403, detail="Отказано в доступе!")
    elif role_id == 2:
        # Check if user manages the project this defect belongs to
        project = db.query(Project).filter(Project.id == defect.project_id).first()
        if not project or project.manager_id != user_id:
            raise HTTPException(status_code=403, detail="Отказано в доступе!")

    # Get project and creator info
    project = db.query(Project).filter(Project.id == defect.project_id).first()
    creator = db.query(User).filter(User.id == defect.creator_id).first()

    return {
        "id": defect.id,
        "title": defect.title,
        "description": defect.description,
        "status": defect.status.value,
        "priority": defect.priority.value,
        "assignee": defect.assignee,
        "due_date": defect.due_date.isoformat() if defect.due_date else None,
        "attachments": defect.attachments or [],
        "project_id": defect.project_id,
        "project_name": project.name if project else "Неизвестно",
        "creator_id": defect.creator_id,
        "creator_name": f"{creator.profile.first_name} {creator.profile.last_name}" if creator and creator.profile else "Неизвестно"
    }
