from fastapi import HTTPException, Depends, APIRouter
from app.db.models import Bid
from app.db.schemas import BidSchema
from app.db.database import SessionLocal
from sqlalchemy.orm import Session
from typing import List


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

bid_router = APIRouter(
    prefix='/bid',
    tags=['Bid']
)




@bid_router.post('/create/', response_model=BidSchema)
async def create_bid(bid: BidSchema, db: Session = Depends(get_db)):

    last_bid = db.query(Bid).filter(Bid.auction_id == bid.auction_id).order_by(Bid.amount.desc()).first()
    if last_bid and bid.amount <= last_bid.amount:
        raise HTTPException(status_code=400, detail="Ставка чон болуш керек")
    bid_db = Bid(
        amount=bid.amount,
        auction_id=bid.auction_id,
        buyer_id=bid.buyer_id
    )
    db.add(bid_db)
    db.commit()
    db.refresh(bid_db)
    return bid_db



@bid_router.get('/list/', response_model=List[BidSchema])
async def last_bid(db: Session = Depends(get_db)):
   return db.query(Bid).all()


@bid_router.get('/{bid_id}/')
async def detail_bid(bid_id: int, db: Session = Depends(get_db)):
   bid_db =  db.query(Bid).filter(Bid.id == bid_id).first()
   if bid_db is None:
       raise HTTPException(status_code=404, detail='категория жок')
   return bid_db


@bid_router.put('/{bid_id}/', response_model=dict)
async def update_bid(bid: BidSchema, bid_id: int,
                          db: Session = Depends(get_db)):
   bid_db =  db.query(Bid).filter(Bid.id == bid_id).first()
   if bid_db is None:
       raise HTTPException(status_code=404, detail='not a data')
   bid_db.amount = bid.amount
   db.add(bid_db)
   db.commit()
   db.refresh(bid_db)
   return {'message': 'Update'}


@bid_router.delete('/{bid_id}/')
async def delete_bid(bid_id: int, db: Session = Depends(get_db)):
   bid_db =  db.query(Bid).filter(Bid.id == bid_id).first()
   if bid_db is None:
       raise HTTPException(status_code=404, detail='категория жок')
   db.delete(bid_db)
   db.commit()
   return {'message': 'Delete'}