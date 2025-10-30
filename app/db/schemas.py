from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from app.db.models import StatusChoices, StatusAuctionChoices
from datetime import datetime



class UserProfileOutSchema(BaseModel):
    id: int
    user_name: str
    email: EmailStr
    age: Optional[int]
    phone_number: Optional[int]
    status : StatusChoices
    created_date : datetime
    password: str

    class Config:
        from_attributes = True


class UserProfileCreateSchema(BaseModel):
    user_name: str
    email: EmailStr
    age: Optional[int] = None
    phone_number: Optional[int] = None
    status: StatusChoices
    password: str

    class Config:
        from_attributes = True


class UserProfileLoginSchema(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class BrandSchema(BaseModel):
    id: int
    brand_name: str

    class Config:
        from_attributes = True


class ModelSchema(BaseModel):
    id: int
    model_name: str
    brand_id: int

    class Config:
        from_attributes = True


class CarSchema(BaseModel):
    id: int
    year: int
    fuel_type: str
    transmission: str
    mileage: int
    price: float
    description: str
    seller: StatusChoices
    brand_id: int
    model_id: int

    class Config:
        from_attributes = True


class CarImageSchema(BaseModel):
    id: int
    car_image: str
    car_id: int


    class Config:
        from_attributes = True


class AuctionSchema(BaseModel):
    id: int
    start_price: float
    min_price: float
    start_time: datetime
    end_time: datetime
    status: StatusAuctionChoices
    car_id: int


    class Config:
        from_attributes = True


class BidSchema(BaseModel):
    id: int
    amount: float
    created_add: datetime
    auction_id: int
    buyer_id: int


    class Config:
        from_attributes = True


class FeedbackSchema(BaseModel):
    id: int
    rating: int = Field(None, gt=0, lt=6)
    comment: str
    created_add: datetime
    buyer_id: int
    seller_id: int


    class Config:
        from_attributes = True