from fastapi import FastAPI, HTTPException, Depends, APIRouter
from app.db.models import Car
from app.db.schemas import CarSchema
from app.db.database import SessionLocal
from sqlalchemy.orm import Session
from typing import List

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

car_router = APIRouter(
    prefix='/car',
    tags=['Car']
)

@car_router.post('/create/', response_model=CarSchema)
async def car_create(car: CarSchema, db: Session = Depends(get_db)):
    car_db = Car(**car.dict())
    db.add(car_db)
    db.commit()
    db.refresh(car_db)
    return car_db


@car_router.get('/car', response_model=List[CarSchema])
async def last_car(db: Session = Depends(get_db)):
   return db.query(Car).all()


@car_router.get('/{car_id}/')
async def detail_car(car_id: int, db: Session = Depends(get_db)):
   car_db =  db.query(Car).filter(Car.id == car_id).first()
   if car_db is None:
       raise HTTPException(status_code=404, detail='car not')
   return car_db


@car_router.put('/{car_id}/', response_model=dict)
async def update_car(car: CarSchema, car_id: int,
                          db: Session = Depends(get_db)):
   car_db =  db.query(Car).filter(Car.id == car_id).first()
   if car_db is None:
       raise HTTPException(status_code=404, detail='not a data')
   car_db.fuel_type = car.fuel_type
   db.add(car_db)
   db.commit()
   db.refresh(car_db)
   return {'message': 'Update'}



@car_router.delete('/{car_id}/')
async def delete_car(car_id: int, db: Session = Depends(get_db)):
   car_db =  db.query(Car).filter(Car.id == car_id).first()
   if car_db is None:
       raise HTTPException(status_code=404, detail='продукт жок')
   db.delete(car_db)
   db.commit()
   return {'message': 'Delete'}