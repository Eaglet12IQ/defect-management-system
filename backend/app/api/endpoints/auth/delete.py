from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User

router = APIRouter()

@router.delete("/delete")
async def delete(response: Response, request: Request, db: Session = Depends(get_db)):
    return User.delete(db, response, request)
    
