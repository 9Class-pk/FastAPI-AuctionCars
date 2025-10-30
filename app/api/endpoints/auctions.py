from fastapi import HTTPException, Depends, APIRouter
from app.db.models import Auction
from app.db.schemas import AuctionSchema
from app.db.database import SessionLocal
from sqlalchemy.orm import Session
from typing import List


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

auction_router = APIRouter(
    prefix='/auction',
    tags=['Auction']
)


@auction_router.post('/create/', response_model=AuctionSchema)
async def create_auction(auction: AuctionSchema, db: Session = Depends(get_db)):
    auction_db = Auction(
        start_price=auction.start_price,
        min_price=auction.min_price,
        start_time=auction.start_time,
        end_time=auction.end_time,
        status=auction.status,
        car_id=auction.car_id
    )
    db.add(auction_db)
    db.commit()
    db.refresh(auction_db)
    return auction_db


@auction_router.get('/list/', response_model=List[AuctionSchema])
async def last_auction(db: Session = Depends(get_db)):
   return db.query(Auction).all()


@auction_router.get('/{auction_id}/')
async def detail_auction(auction_id: int, db: Session = Depends(get_db)):
   auction_db =  db.query(Auction).filter(Auction.id == auction_id).first()
   if auction_db is None:
       raise HTTPException(status_code=404, detail='категория жок')
   return auction_db


@auction_router.put('/{auction_id}/', response_model=dict)
async def update_auction(auction: AuctionSchema, auction_id: int,
                          db: Session = Depends(get_db)):
   auction_db =  db.query(Auction).filter(Auction.id == auction_id).first()
   if auction_db is None:
       raise HTTPException(status_code=404, detail='not a data')
   auction_db.start_price = auction.start_price
   db.add(auction_db)
   db.commit()
   db.refresh(auction_db)
   return {'message': 'Update'}


@auction_router.delete('/{auction_id}/')
async def delete_auction(auction_id: int, db: Session = Depends(get_db)):
   auction_db =  db.query(Auction).filter(Auction.id == auction_id).first()
   if auction_db is None:
       raise HTTPException(status_code=404, detail='категория жок')
   db.delete(auction_db)
   db.commit()
   return {'message': 'Delete'}