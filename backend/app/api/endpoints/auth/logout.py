from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.core.security import (
    SECRET_KEY,
    ALGORITHM
)
from jose import jwt, ExpiredSignatureError, JWTError

router = APIRouter()

@router.post("/logout")
async def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    return User.logout(db, request, response)
