from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class FeedbackBase(BaseModel):
    seller_id: int
    rating: int
    comment: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackInDB(FeedbackBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    buyer_id: int
    created_at: datetime

class FeedbackResponse(FeedbackInDB):
    pass

class FeedbackListResponse(BaseModel):
    count: int
    average_rating: float
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[FeedbackResponse]