from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
import json
from app.core.database import get_db
from app.core.security import get_current_user
from app.schema.car import CarCreate, CarResponse, CarListResponse
from app.models.user import User, UserRole
from app.models.car import Car
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=CarListResponse)
def get_cars(
        skip: int = 0,
        limit: int = 10,
        brand: Optional[str] = Query(None),
        model: Optional[str] = Query(None),
        year_min: Optional[int] = Query(None),
        year_max: Optional[int] = Query(None),
        price_min: Optional[float] = Query(None),
        price_max: Optional[float] = Query(None),
        fuel_type: Optional[str] = Query(None),
        transmission: Optional[str] = Query(None),
        db: Session = Depends(get_db)
):
    query = db.query(Car)

    # Apply filters
    if brand:
        query = query.filter(Car.brand.ilike(f"%{brand}%"))
    if model:
        query = query.filter(Car.model.ilike(f"%{model}%"))
    if year_min:
        query = query.filter(Car.year >= year_min)
    if year_max:
        query = query.filter(Car.year <= year_max)
    if price_min:
        query = query.filter(Car.price >= price_min)
    if price_max:
        query = query.filter(Car.price <= price_max)
    if fuel_type:
        query = query.filter(Car.fuel_type == fuel_type)
    if transmission:
        query = query.filter(Car.transmission == transmission)

    total = query.count()
    cars = query.offset(skip).limit(limit).all()

    return CarListResponse(
        count=total,
        next=None,  # Implement pagination logic
        previous=None,
        results=cars
    )


@router.post("/", response_model=CarResponse)
def create_car(
        car_data: CarCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.SELLER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can create cars"
        )

    car = Car(**car_data.dict(), seller_id=current_user.id)
    db.add(car)
    db.commit()
    db.refresh(car)

    return car


@router.get("/{car_id}", response_model=CarResponse)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    return car