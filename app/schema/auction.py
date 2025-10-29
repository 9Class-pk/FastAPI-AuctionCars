from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.auction import AuctionStatus

class AuctionBase(BaseModel):
    car_id: int
    start_price: float
    min_price: float
    start_time: datetime
    end_time: datetime

class AuctionCreate(AuctionBase):
    pass

class AuctionUpdate(BaseModel):
    start_price: Optional[float] = None
    min_price: Optional[float] = None
    end_time: Optional[datetime] = None
    status: Optional[AuctionStatus] = None

class AuctionInDB(AuctionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    current_price: float
    status: AuctionStatus
    created_at: datetime

class AuctionResponse(AuctionInDB):
    pass

class AuctionListResponse(BaseModel):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[AuctionResponse]