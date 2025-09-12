from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.stamp import Stamp
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, status
from app.models.collector import Collector
from app.models.collection import Collection
from app.core.security import get_payload_from_refresh_token
import os
import shutil

router = APIRouter()

AVATAR_UPLOAD_DIR = "static/stamps"

@router.get("/top_expensive")
async def get_top_expensive_stamps(db: Session = Depends(get_db)):
    stamps = db.query(Stamp).order_by(Stamp.cost.desc()).limit(3).all()
    result = []
    for stamp in stamps:
        result.append({
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
        })
    return result

@router.get("/grouped_rare")
async def get_rare_stamps_grouped(db: Session = Depends(get_db)):
    collectors = db.query(Collector).all()

    result = []
    for collector in collectors:
        rare_stamps = []
        for collection in collector.collections:
            for stamp in collection.stamps:
                if stamp.cost > 1000:
                    rare_stamps.append({
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
                        "rarity": "Редкая"
                    })
        if rare_stamps:
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
                "following": 0,
                "followers": 0,
                "rare_stamps": rare_stamps
            })

    return result

@router.get("/{stamp_id}")
async def get_stamp_by_id(stamp_id: int, db: Session = Depends(get_db)):
    stamp = db.query(Stamp).filter(Stamp.id == stamp_id).first()
    if not stamp:
        raise HTTPException(status_code=404, detail="Stamp not found")

    collection = db.query(Collection).filter(Collection.id == stamp.collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    return {
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
        "rarity": "Редкая" if stamp.cost > 1000 else "Обычная",
        "collection_id": stamp.collection_id,
        "collector_id": collection.collector_id  # 👈 добавлено
    }

@router.get("/")
async def get_all_stamps(db: Session = Depends(get_db)):
    stamps = db.query(Stamp).all()
    result = []
    for stamp in stamps:
        result.append({
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
        })
    return result

@router.post("/create")
async def create_stamp(
    request: Request,
    name: str = Form(...),
    serial_number: str = Form(...),
    country: str = Form(...),
    year: int = Form(...),
    circulation: int = Form(...),
    cost: float = Form(...),
    perforation: str = Form(...),
    topic: str = Form(...),
    features: str = Form(...),
    collection_id: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Check collection ownership
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=403, detail="Коллекции с таким айди не существует!")
    
    payload = get_payload_from_refresh_token(request)
    access_user_id = payload.get("sub")
    collector = Collector.get_collector(db, access_user_id)

    if collection.collector_id != collector.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа!")

    # Check for unique serial_number
    existing_stamp = db.query(Stamp).filter(Stamp.serial_number == serial_number).first()
    if existing_stamp:
        raise HTTPException(status_code=400, detail="Марка с таким серийным номером уже существует.")

    new_stamp = Stamp(
        name=name,
        serial_number=serial_number,
        country=country,
        year=year,
        circulation=circulation,
        cost=cost,
        perforation=perforation,
        topic=topic,
        features=features,
        photo_url="/static/avatars/default_avatar.png",
        collection_id=collection_id
    )
    db.add(new_stamp)
    db.commit()
    db.refresh(new_stamp)

    # Сохраняем файл
    file_extension = os.path.splitext(image.filename)[1]
    filename = f"{new_stamp.id}{file_extension}"
    file_path = os.path.join(AVATAR_UPLOAD_DIR, filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save avatar file.")

    new_stamp.photo_url = f"/{AVATAR_UPLOAD_DIR}/{filename}"
    db.commit()
    db.refresh(new_stamp)
    return {
        "id": new_stamp.id,
        "name": new_stamp.name,
        "serial_number": new_stamp.serial_number,
        "country": new_stamp.country,
        "year": new_stamp.year,
        "circulation": new_stamp.circulation,
        "cost": new_stamp.cost,
        "perforation": new_stamp.perforation,
        "topic": new_stamp.topic,
        "features": new_stamp.features,
        "photo_url": f"http://localhost:8000{new_stamp.photo_url}",
        "rarity": "Редкая" if new_stamp.cost > 1000 else "Обычная"
    }

@router.delete("/delete/{stamp_id}")
async def delete_stamp(stamp_id: int, request: Request, db: Session = Depends(get_db)):
    stamp = db.query(Stamp).filter(Stamp.id == stamp_id).first()
    if not stamp:
        raise HTTPException(status_code=404, detail="Stamp not found")

    collection = db.query(Collection).filter(Collection.id == stamp.collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    payload = get_payload_from_refresh_token(request)
    access_user_id = payload.get("sub")
    collector = Collector.get_collector(db, access_user_id)

    if collection.collector_id != collector.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа!")

    # Delete the stamp photo file if exists
    photo_path = stamp.photo_url.lstrip('/')
    if os.path.exists(photo_path):
        try:
            os.remove(photo_path)
        except Exception:
            pass

    db.delete(stamp)
    db.commit()

    return {"detail": "Stamp deleted successfully"}

@router.patch("/update/{stamp_id}")
async def update_stamp(
    stamp_id: int,
    request: Request,
    name: str = Form(...),
    serial_number: str = Form(...),
    country: str = Form(...),
    year: int = Form(...),
    circulation: int = Form(...),
    cost: float = Form(...),
    perforation: str = Form(...),
    topic: str = Form(...),
    features: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    stamp = db.query(Stamp).filter(Stamp.id == stamp_id).first()
    if not stamp:
        raise HTTPException(status_code=404, detail="Stamp not found")

    collection = db.query(Collection).filter(Collection.id == stamp.collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    payload = get_payload_from_refresh_token(request)
    access_user_id = payload.get("sub")
    collector = Collector.get_collector(db, access_user_id)

    if collection.collector_id != collector.user_id:
        raise HTTPException(status_code=403, detail="Нет доступа!")

    stamp.name = name
    stamp.serial_number = serial_number
    stamp.country = country
    stamp.year = year
    stamp.circulation = circulation
    stamp.cost = cost
    stamp.perforation = perforation
    stamp.topic = topic
    stamp.features = features

    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Only images are allowed.")

        file_extension = os.path.splitext(image.filename)[1]
        filename = f"{stamp.id}{file_extension}"
        file_path = os.path.join(AVATAR_UPLOAD_DIR, filename)
        
        if stamp.photo_url:
            old_filename = os.path.basename(stamp.photo_url)
            old_path = os.path.join(AVATAR_UPLOAD_DIR, old_filename)
            if os.path.exists(old_path) and old_path != file_path and old_path != "static/avatars\default_avatar.png":
                os.remove(old_path)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save avatar file.")

        stamp.photo_url = f"/{AVATAR_UPLOAD_DIR}/{filename}"

    db.commit()
    db.refresh(stamp)

    return {
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
