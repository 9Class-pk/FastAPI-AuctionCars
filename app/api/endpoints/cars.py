from fastapi import FastAPI, HTTPException, Depends, APIRouter
from app.db.models import Car
from app.db.schemas import CarSchema
from app.db.database import SessionLocal
from sqlalchemy.orm import Session
from typing import List
from fastapi import Query


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
async def create_car(car: CarSchema, db: Session = Depends(get_db)):
    car_db = Car(**car.dict())
    db.add(car_db)
    db.commit()
    db.refresh(car_db)
    return car_db


@car_router.get('/', response_model=List[CarSchema])
async def list_car(db: Session = Depends(get_db),
    year_from: int | None = Query(None),
    year_to: int | None = Query(None),
    mileage_max: int | None = Query(None),
    status: str | None = Query(None),
    brand: str | None = Query(None),
    model: str | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
    ):


    query = db.query(Car)

    # фильтры
    if year_from:
        query = query.filter(Car.year >= year_from)
    if year_to:
        query = query.filter(Car.year <= year_to)
    if mileage_max:
        query = query.filter(Car.mileage <= mileage_max)
    if status:
        query = query.filter(Car.status == status)
    if brand:
        query = query.filter(Car.brand.ilike(f"%{brand}%"))
    if model:
        query = query.filter(Car.model.ilike(f"%{model}%"))

    # поиск
    if search:
        query = query.filter(
            (Car.name.ilike(f"%{search}%")) |
            (Car.description.ilike(f"%{search}%"))
        )

    # сортировка
    if sort_by in ["price", "year", "created_at"]:
        column = getattr(Car, sort_by)
        if sort_order == "desc":
            column = column.desc()
        query = query.order_by(column)

    total = query.count()
    results = query.offset(offset).limit(limit).all()

    return {"total": total, "items": results}




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