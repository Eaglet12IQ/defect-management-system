from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.collector import Collector
import os
import shutil
import uuid
from app.core.security import get_payload_from_refresh_token

router = APIRouter()

AVATAR_UPLOAD_DIR = "static/avatars"

@router.patch("/avatar", summary="Change user avatar")
async def change_avatar(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    payload = get_payload_from_refresh_token(request)
    access_user_id = payload.get("sub")
    current_user = Collector.get_collector(db, access_user_id)
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Only images are allowed.")

    # Use user_id as filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{access_user_id}{file_extension}"
    file_path = os.path.join(AVATAR_UPLOAD_DIR, filename)

    # Delete old avatar file if it has different extension
    if current_user.avatar_url:
        old_filename = os.path.basename(current_user.avatar_url)
        old_path = os.path.join(AVATAR_UPLOAD_DIR, old_filename)
        if os.path.exists(old_path) and old_path != file_path and old_path != "static/avatars\default_avatar.png":
            os.remove(old_path)

    # Save new file (overwrite if exists)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save avatar file.")

    # Update avatar URL in DB
    new_avatar_url = f"/{AVATAR_UPLOAD_DIR}/{filename}"
    current_user.avatar_url = new_avatar_url
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Avatar updated successfully",
            "avatar_url": f"http://localhost:8000{new_avatar_url}"
        }
    )

