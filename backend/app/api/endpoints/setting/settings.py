from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.collector import Collector
from app.models.user import User
from app.models.collection import Collection
from app.core.security import get_payload_from_refresh_token

router = APIRouter()

@router.get("/user")
async def get_user_settings(request: Request, db: Session = Depends(get_db)):
    payload = get_payload_from_refresh_token(request)
    access_user_id = payload.get("sub")
    user = User.get_user(db, access_user_id)

    return {
        "username": user.username,
        "email": user.email
    }

@router.get("/collector")
async def get_collector_settings(request: Request, db: Session = Depends(get_db)):
    payload = get_payload_from_refresh_token(request)
    access_user_id = payload.get("sub")
    collector = Collector.get_collector(db, access_user_id)

    return {
        "country": collector.country,
        "phone_number": collector.phone_number,
        "last_name": collector.last_name,
        "first_name": collector.first_name,
        "middle_name": collector.middle_name
    }
