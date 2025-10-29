from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class BidBase(BaseModel):
    auction_id: int
    amount: float

class BidCreate(BidBase):
    pass

class BidInDB(BidBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    buyer_id: int
    is_winning: bool
    created_at: datetime

class BidResponse(BidInDB):
    pass