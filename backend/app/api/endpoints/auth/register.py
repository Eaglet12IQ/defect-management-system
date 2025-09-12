from fastapi import APIRouter, Depends, HTTPException, Response
from app.schemas.user import UserCreateWithPasswordValidation
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User

router = APIRouter()

@router.post("/register")
async def register(response: Response, user: UserCreateWithPasswordValidation, db: Session = Depends(get_db)):
    return User.register(db, response, user)