from fastapi import APIRouter, Depends, Response, Request, Form, File, HTTPException
from app.schemas.user import UserLoginWithPasswordValidation
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from fastapi.datastructures import UploadFile as UploadFileType
from app.core.security import get_payload_from_refresh_token

router = APIRouter()

@router.post("/login")
async def login(response: Response, user: UserLoginWithPasswordValidation, db: Session = Depends(get_db)):
    return User.login(db, response, user)
    
@router.delete("/delete")
async def delete(response: Response, request: Request, db: Session = Depends(get_db)):
    return User.delete(db, response, request)

@router.post("/logout")
async def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    return User.logout(db, request, response)

@router.post("/register")
async def register(
    response: Response,
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    re_password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    middle_name: str = Form(None),
    role: int = Form(...),
    avatar: UploadFileType = File(None),
    db: Session = Depends(get_db)
):
    payload = get_payload_from_refresh_token(request)
    role_id = payload.get("role")
    if role_id != 4:
        raise HTTPException(status_code=403, detail="Отказано в доступе!")
    return User.register(db, response, username, email, password, re_password, first_name, last_name, middle_name, role, avatar)
