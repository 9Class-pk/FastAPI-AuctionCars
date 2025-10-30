from fastapi import HTTPException, Depends, APIRouter, Security
from app.db.models import UserProfile
from app.db.schemas import UserProfileSchema
from app.db.database import  SessionLocal
from sqlalchemy.orm import Session
from typing import List




async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


user_router = APIRouter(prefix='/user', tags=['UserProfile'])


@user_router.post("/", response_model=UserProfileSchema)
async def create_user(user_data: UserProfileSchema, db:Session = Depends(get_db)):
    user_db = UserProfile(**user_data.dict())
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db

@user_router.get("/", response_model=List[UserProfileSchema])
async def list_user(db: Session = Depends(get_db)):

    return db.query(UserProfile).all()


@user_router.get("/{user_id}/", response_model=UserProfileSchema)
async def detail_user(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.id==user_id).first()
    if user_db is None:
        raise HTTPException(status_code=404, detail='Нету такого пользователя')
    return user_db


@user_router.put("/{user_id}/")
async def update_user(user_data: UserProfileSchema, user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Нету такого пользователя'")

    for user_key, user_value in user_data.dict().items():
        setattr(user_db, user_key, user_value)

    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db


@user_router.delete("/{user_id}/")
async def delete_user(user_id: int, db:Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if user_db is None:
        raise HTTPException(status_code=404, detail='Нету такой категории')
    db.delete(user_db)
    db.commit()
    return  {'message': 'Deleted'}