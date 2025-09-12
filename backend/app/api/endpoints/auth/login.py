from fastapi import APIRouter, Depends, HTTPException, Response
from app.schemas.user import UserLoginWithPasswordValidation
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User

router = APIRouter()

@router.post("/login")
async def login(response: Response, user: UserLoginWithPasswordValidation, db: Session = Depends(get_db)):
    return User.login(db, response, user)
    
