from fastapi import HTTPException, Depends, APIRouter
from app.db.models import Brand
from app.db.schemas import BrandSchema
from app.db.database import SessionLocal
from sqlalchemy.orm import Session
from typing import List


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

brand_router = APIRouter(
    prefix='/brand',
    tags=['Brand']
)


@brand_router.post('/create/', response_model=BrandSchema)
async def create_brand(brand: BrandSchema, db: Session = Depends(get_db)):
    brand_db = Brand(brand_name = brand.brand_name)
    db.add(brand_db)
    db.commit()
    db.refresh(brand_db)
    return brand_db


@brand_router.get('/list/', response_model=List[BrandSchema])
async def last_brand(db: Session = Depends(get_db)):
   return db.query(Brand).all()


@brand_router.get('/{brand_id}/')
async def detail_brand(brand_id: int, db: Session = Depends(get_db)):
   brand_db =  db.query(Brand).filter(Brand.id == brand_id).first()
   if brand_db is None:
       raise HTTPException(status_code=404, detail='категория жок')
   return brand_db


@brand_router.put('/{brand_id}/', response_model=dict)
async def update_brand(brand: BrandSchema, brand_id: int,
                          db: Session = Depends(get_db)):
   brand_db =  db.query(Brand).filter(Brand.id == brand_id).first()
   if brand_db is None:
       raise HTTPException(status_code=404, detail='not a data')
   brand_db.brand_name = brand.brand_name
   db.add(brand_db)
   db.commit()
   db.refresh(brand_db)
   return {'message': 'Update'}


@brand_router.delete('/{brand_id}/')
async def delete_brand(brand_id: int, db: Session = Depends(get_db)):
   brand_db =  db.query(Brand).filter(Brand.id == brand_id).first()
   if brand_db is None:
       raise HTTPException(status_code=404, detail='категория жок')
   db.delete(brand_db)
   db.commit()
   return {'message': 'Delete'}