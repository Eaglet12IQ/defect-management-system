from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.collector import Collector
from jose import JWTError, jwt

SECRET_KEY = "АФК ЛЕГЕНДА ДОТЫ"
ALGORITHM = "HS256"

router = APIRouter()

def get_payload_from_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def verify_admin(db: Session, token: str):
    payload = get_payload_from_access_token(token)
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role_id != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden: Admins only")
    return user

@router.get("/users")
async def get_users_list(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.split(" ")[1] if authorization else ""
    verify_admin(db, token)
    users = db.query(User).all()
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.name if user.role else None
        })
    return result

@router.get("/collectors")
async def get_collectors_list(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.split(" ")[1] if authorization else ""
    verify_admin(db, token)
    collectors = db.query(Collector).all()
    result = []
    for collector in collectors:
        result.append({
            "id": collector.user_id,
            "username": collector.user.username,
            "avatar_url": f"http://localhost:8000{collector.avatar_url}",
            "country": collector.country,
            "phone_number": collector.phone_number,
            "first_name": collector.first_name,
            "last_name": collector.last_name,
            "middle_name": collector.middle_name,
            "email": collector.user.email
        })
    return result
