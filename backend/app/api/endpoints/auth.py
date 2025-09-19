from fastapi import APIRouter, Depends, Response, Request, Form, File
from app.schemas.user import UserLoginWithPasswordValidation
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from fastapi.datastructures import UploadFile as UploadFileType

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
    return User.register(db, response, username, email, password, re_password, first_name, last_name, middle_name, role, avatar)
