from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.profile import Profile
from app.core.security import get_payload_from_refresh_token

router = APIRouter()

@router.get("/dashboard")
async def dashboard(response: Response, request: Request, db: Session = Depends(get_db)):
    payload = get_payload_from_refresh_token(request)
    access_user_id = payload.get("sub")
    role_id = payload.get("role")
    
    data = {}

    profile = Profile.get_profile(db, access_user_id)
    fio_parts = [profile.last_name, profile.first_name]
    if profile.middle_name:
        fio_parts.append(profile.middle_name)
    data["fio"] = " ".join(fio_parts)

    return data