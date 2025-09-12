from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.collector import Collector
from app.models.collection import Collection
from app.core.security import get_payload_from_refresh_token
import os
import shutil

router = APIRouter()
AVATAR_UPLOAD_DIR = "static/collections"

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.collector import Collector
from app.models.collection import Collection
from app.models.stamp import Stamp
from app.core.security import get_payload_from_refresh_token
import os
import shutil

router = APIRouter()
AVATAR_UPLOAD_DIR = "static/collections"

@router.get("/top_expensive")
async def get_top_expensive_collections(db: Session = Depends(get_db)):
    collections = (
        db.query(
            Collection,
            func.coalesce(func.sum(func.coalesce(Stamp.cost, 0)), 0).label("total_cost")
        )
        .outerjoin(Stamp, Stamp.collection_id == Collection.id)
        .group_by(Collection.id)
        .order_by(func.coalesce(func.sum(func.coalesce(Stamp.cost, 0)), 0).desc())
        .limit(2)
        .all()
    )
    result = []
    for collection, total_cost in collections:
        result.append({
            "id": collection.id,
            "collector_id": collection.collector_id,
            "name": collection.name,
            "description": collection.description,
            "photo_url": f"http://localhost:8000{collection.photo_url}",
            "total_cost": total_cost
        })
    return result

@router.post("/create")
async def create_collection(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    payload = get_payload_from_refresh_token(request)
    access_user_id = payload.get("sub")
    collector = Collector.get_collector(db, access_user_id)

    new_collection = Collection(
        collector_id=collector.user_id,
        name=name,
        description=description,
        photo_url="/static/avatars/default_avatar.png"
    )

    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)

    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Only images are allowed.")

        file_extension = os.path.splitext(image.filename)[1]
        filename = f"{new_collection.id}{file_extension}"
        file_path = os.path.join(AVATAR_UPLOAD_DIR, filename)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save avatar file.")

        new_collection.photo_url = f"/{AVATAR_UPLOAD_DIR}/{filename}"
        db.commit()

    return {
        "id": new_collection.id,
        "collector_id": new_collection.collector_id,
        "name": new_collection.name,
        "description": new_collection.description,
        "photo_url": f"http://localhost:8000{new_collection.photo_url}",
    }

@router.get("")
async def get_collections(db: Session = Depends(get_db)):
    collections = db.query(Collection).all()

    serialized_collections = []
    for collection in collections:
        serialized_collections.append({
            "id": collection.id,
            "collector_id": collection.collector_id,    
            "name": collection.name,
            "description": collection.description,
            "photo_url": f"http://localhost:8000{collection.photo_url}"
        })

    return serialized_collections

@router.get("/grouped")
async def get_collections_grouped(db: Session = Depends(get_db)):
    collectors = db.query(Collector).all()

    result = []
    for collector in collectors:
        if not collector.collections or len(collector.collections) == 0:
            continue
        collections = [
            {
                "id": collection.id,
                "name": collection.name,
                "description": collection.description,
                "photo_url": f"http://localhost:8000{collection.photo_url}"
            }
            for collection in collector.collections
        ]
        result.append({
            "collector_id": collector.user_id,
            "username": collector.user.username,
            "avatar_url": f"http://localhost:8000{collector.avatar_url}",
            "country": collector.country,
            "first_name": collector.first_name,
            "last_name": collector.last_name,
            "middle_name": collector.middle_name,
            "bio": collector.bio if hasattr(collector, 'bio') else '',
            "location": collector.location if hasattr(collector, 'location') else '',
            "memberSince": collector.member_since if hasattr(collector, 'member_since') else '',
            "collectionCount": len(collector.collections) if hasattr(collector, 'collections') else 0,
            "stampCount": sum(len(collection.stamps) for collection in collector.collections) if hasattr(collector, 'collections') else 0,
            "specialties": collector.specialties if hasattr(collector, 'specialties') else [],
            "following": 0,  # Placeholder, implement if needed
            "followers": 0,  # Placeholder, implement if needed
            "collections": collections
        })

    return result

@router.get("/{collection_id}")
async def get_collection_by_id(collection_id: str, db: Session = Depends(get_db)):
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    return {
        "id": collection.id,
        "collector_id": collection.collector_id,
        "name": collection.name,
        "description": collection.description,
        "photo_url": f"http://localhost:8000{collection.photo_url}",
        "stamps": [
            {
                "id": stamp.id,
                "name": stamp.name,
                "serial_number": stamp.serial_number,
                "country": stamp.country,
                "year": stamp.year,
                "circulation": stamp.circulation,
                "cost": stamp.cost,
                "perforation": stamp.perforation,
                "topic": stamp.topic,
                "features": stamp.features,
                "photo_url": f"http://localhost:8000{stamp.photo_url}",
                "rarity": "Редкая" if stamp.cost > 1000 else "Обычная"
            }
            for stamp in collection.stamps
        ]
    }

@router.delete("/delete/{collection_id}", status_code=204)
async def delete_collection(collection_id: str, request: Request, db: Session = Depends(get_db)):
    payload = get_payload_from_refresh_token(request)
    access_user_id = payload.get("sub")
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    if collection.collector_id != int(access_user_id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this collection")

    db.delete(collection)
    db.commit()
    return

@router.patch("/update/{collection_id}")
async def update_collection(
    collection_id: str,
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    payload = get_payload_from_refresh_token(request)
    access_user_id = payload.get("sub")
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    if collection.collector_id != int(access_user_id):
        raise HTTPException(status_code=403, detail="Not authorized to update this collection")

    collection.name = name
    collection.description = description

    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Only images are allowed.")

        file_extension = os.path.splitext(image.filename)[1]
        filename = f"{collection.id}{file_extension}"
        file_path = os.path.join(AVATAR_UPLOAD_DIR, filename)

        if collection.photo_url:
            old_filename = os.path.basename(collection.photo_url)
            old_path = os.path.join(AVATAR_UPLOAD_DIR, old_filename)
            if os.path.exists(old_path) and old_path != file_path and old_path != "static/avatars\default_avatar.png":
                os.remove(old_path)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save avatar file.")

        collection.photo_url = f"/{AVATAR_UPLOAD_DIR}/{filename}"

    db.commit()
    db.refresh(collection)

    return {
        "id": collection.id,
        "collector_id": collection.collector_id,
        "name": collection.name,
        "description": collection.description,
        "photo_url": f"http://localhost:8000{collection.photo_url}",
    }


