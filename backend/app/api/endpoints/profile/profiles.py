from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.collector import Collector
from app.models.user import User
from app.models.collection import Collection
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from sqlalchemy import func

router = APIRouter()

class UserUpdateSchema(BaseModel):
    username: Optional[constr(min_length=3, max_length=50)] = None
    email: Optional[EmailStr] = None

class CollectorUpdateSchema(BaseModel):
    country: Optional[constr(max_length=100)] = None
    phone_number: Optional[constr(max_length=20)] = None
    first_name: Optional[constr(max_length=50)] = None
    last_name: Optional[constr(max_length=50)] = None
    middle_name: Optional[constr(max_length=50)] = None


@router.get("/list")
async def get_collectors_list(db: Session = Depends(get_db)):
    collectors = db.query(Collector).all()
    result = []
    for collector in collectors:
        result.append({
            "id": collector.user_id,
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
            "featured": False  # Placeholder, implement if needed
        })
    return result

@router.get("/most_expensive_stamp_collector")
async def get_collector_with_most_expensive_stamp(db: Session = Depends(get_db)):
    # Query to find the stamp with the highest cost
    from app.models.stamp import Stamp
    most_expensive_stamp = db.query(Stamp).order_by(Stamp.cost.desc()).first()
    if not most_expensive_stamp:
        return {"message": "No stamps found"}

    # Get the collector who owns this stamp
    collection = db.query(Collection).filter(Collection.id == most_expensive_stamp.collection_id).first()
    if not collection:
        return {"message": "Collection not found for the most expensive stamp"}

    collector = db.query(Collector).filter(Collector.user_id == collection.collector_id).first()
    if not collector:
        return {"message": "Collector not found for the most expensive stamp"}

    return {
        "id": collector.user_id,
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
        "featured": False
    }

@router.get("/max_rare_stamp_collector")
async def get_collector_with_max_rare_stamps(db: Session = Depends(get_db)):
    from app.models.stamp import Stamp

    RARITY_THRESHOLD = 1000  # Define cost above this as rare

    # Subquery to count rare stamps per collector
    rare_stamps_subq = (
        db.query(
            Collection.collector_id.label("collector_id"),
            func.count(Stamp.id).label("rare_stamp_count")
        )
        .join(Stamp, Stamp.collection_id == Collection.id)
        .filter(Stamp.cost > RARITY_THRESHOLD)
        .group_by(Collection.collector_id)
        .subquery()
    )

    # Find collector with max rare_stamp_count
    max_rare = db.query(
        rare_stamps_subq.c.collector_id,
        rare_stamps_subq.c.rare_stamp_count
    ).order_by(rare_stamps_subq.c.rare_stamp_count.desc()).first()

    if not max_rare:
        return {"message": "No rare stamps found"}

    collector = db.query(Collector).filter(Collector.user_id == max_rare.collector_id).first()
    if not collector:
        return {"message": "Collector not found for max rare stamps"}

    return {
        "id": collector.user_id,
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
        "featured": False
    }

from fastapi import Query

@router.get("/sorted_by_collection_value")
async def get_collectors_sorted_by_collection_value(
    limit: int = Query(None, description="Limit number of collectors returned"),
    db: Session = Depends(get_db)
):
    from app.models.stamp import Stamp
    from sqlalchemy import func

    query = (
        db.query(
            Collector,
            func.coalesce(func.sum(Stamp.cost), 0).label("total_value")
        )
        .outerjoin(Collection, Collection.collector_id == Collector.user_id)
        .outerjoin(Stamp, Stamp.collection_id == Collection.id)
        .group_by(Collector.user_id)
        .order_by(func.coalesce(func.sum(Stamp.cost), 0).desc())
    )

    if limit is not None:
        query = query.limit(limit)

    collectors_with_value = query.all()

    result = []
    for collector, total_value in collectors_with_value:
        result.append({
            "id": collector.user_id,
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
            "featured": False,
            "totalCollectionValue": total_value
        })
    return result

@router.get("/collectors_with_old_stamps")
async def get_collectors_with_old_stamps(db: Session = Depends(get_db)):
    from app.models.stamp import Stamp
    from datetime import datetime, timedelta

    ten_years_ago = datetime.now() - timedelta(days=365*10)
    cutoff_year = ten_years_ago.year

    # Subquery to find collector ids with stamps older than 10 years
    old_stamps_subq = (
        db.query(Collection.collector_id)
        .join(Stamp, Stamp.collection_id == Collection.id)
        .filter(Stamp.year < cutoff_year)
        .distinct()
        .subquery()
    )

    collectors = (
        db.query(Collector)
        .filter(Collector.user_id.in_(old_stamps_subq))
        .all()
    )

    result = []
    for collector in collectors:
        result.append({
            "id": collector.user_id,
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
            "featured": False
        })
    return result

@router.get("/{user_id}")
async def get_profile(user_id: str, db: Session = Depends(get_db)):
    user = User.get_user(db, user_id)
    collector = Collector.get_collector(db, user_id)
    collections = Collection.get_collections(db, user_id)

    serialized_collections = []
    for collection in collections:
        serialized_collections.append({
            "id": collection.id,
            "name": collection.name,
            "description": collection.description,
            "photo_url": f"http://localhost:8000{collection.photo_url}",  # ✅ добавляем префикс
            "collector_id": collection.collector_id
        })

    return {
        "id": user_id,
        "username": user.username,
        "avatar_url": f"http://localhost:8000{collector.avatar_url}",
        "country": collector.country,
        "first_name": collector.first_name,
        "last_name": collector.last_name,
        "middle_name": collector.middle_name,
        "collections": serialized_collections  # ✅ возвращаем кастомные коллекции
    }

@router.patch("/users/{user_id}", status_code=200)
async def update_user(user_id: int, user_update: UserUpdateSchema, db: Session = Depends(get_db)):
    user = User.get_user(db, user_id)
    updated = False
    if user_update.username is not None:
        # Check if username already exists for another user
        existing_user = db.query(User).filter(User.username == user_update.username, User.id != user_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        user.username = user_update.username
        updated = True
    if user_update.email is not None:
        # Check if email already exists for another user
        existing_email_user = db.query(User).filter(User.email == user_update.email, User.id != user_id).first()
        if existing_email_user:
            raise HTTPException(status_code=400, detail="Email already exists")
        user.email = user_update.email
        updated = True
    if updated:
        db.commit()
        db.refresh(user)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }

@router.patch("/collectors/{user_id}", status_code=200)
async def update_collector(user_id: int, collector_update: CollectorUpdateSchema, db: Session = Depends(get_db)):
    collector = Collector.get_collector(db, user_id)
    updated = False
    if collector_update.country is not None:
        collector.country = collector_update.country
        updated = True
    if collector_update.phone_number is not None:
        collector.phone_number = collector_update.phone_number
        updated = True
    if collector_update.first_name is not None:
        collector.first_name = collector_update.first_name
        updated = True
    if collector_update.last_name is not None:
        collector.last_name = collector_update.last_name
        updated = True
    if collector_update.middle_name is not None:
        collector.middle_name = collector_update.middle_name
        updated = True
    if updated:
        db.commit()
        db.refresh(collector)
    return {
        "user_id": collector.user_id,
        "country": collector.country,
        "phone_number": collector.phone_number,
        "first_name": collector.first_name,
        "last_name": collector.last_name,
        "middle_name": collector.middle_name
    }
