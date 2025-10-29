from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.car import FuelType, Transmission, CarCondition


class CarBase(BaseModel):
    brand: str
    model: str
    year: int
    fuel_type: FuelType
    transmission: Transmission
    mileage: Optional[float] = None
    price: float
    description: Optional[str] = None
    condition: CarCondition = CarCondition.GOOD


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    description: Optional[str] = None


class CarInDB(CarBase):
    id: int
    seller_id: int
    images: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CarResponse(CarInDB):
    pass


class CarListResponse(BaseModel):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[CarResponse]