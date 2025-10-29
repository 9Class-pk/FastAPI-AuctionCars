from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.auction import Auction, AuctionStatus
from app.models.bid import Bid
from app.schema.bid import BidCreate, BidResponse
from app.api.v1.auth import get_current_user
from app.services.websocket import websocket_manager

router = APIRouter()


@router.post("/", response_model=BidResponse)
async def create_bid(
        bid_data: BidCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.BUYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyers can place bids"
        )

    # Check auction exists and is active
    result = await db.execute(
        select(Auction).where(
            and_(
                Auction.id == bid_data.auction_id,
                Auction.status == AuctionStatus.ACTIVE,
                Auction.end_time > datetime.utcnow()
            )
        )
    )
    auction = result.scalar_one_or_none()

    if not auction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active auction not found"
        )

    # Check bid amount is higher than current price
    if bid_data.amount <= auction.current_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bid amount must be higher than current price: {auction.current_price}"
        )

    # Check bid amount meets minimum price
    if bid_data.amount < auction.min_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bid amount must be at least minimum price: {auction.min_price}"
        )

    # Create bid
    bid = Bid(
        auction_id=bid_data.auction_id,
        buyer_id=current_user.id,
        amount=bid_data.amount
    )

    # Update auction current price
    auction.current_price = bid_data.amount

    # Set all previous bids as not winning
    await db.execute(
        Bid.__table__.update()
        .where(Bid.auction_id == bid_data.auction_id)
        .values(is_winning=False)
    )

    # Set this bid as winning
    bid.is_winning = True

    db.add(bid)
    await db.commit()
    await db.refresh(bid)

    # Notify via WebSocket
    await websocket_manager.broadcast_to_auction(
        bid_data.auction_id,
        {
            "type": "new_bid",
            "bid_id": bid.id,
            "amount": bid.amount,
            "buyer_id": bid.buyer_id,
            "created_at": bid.created_at.isoformat()
        }
    )

    return bid


@router.get("/my-bids", response_model=List[BidResponse])
async def get_my_bids(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    query = select(Bid).where(Bid.buyer_id == current_user.id).order_by(Bid.created_at.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    bids = result.scalars().all()

    return list(bids)


@router.get("/auction/{auction_id}", response_model=List[BidResponse])
async def get_auction_bids(
        auction_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_db)
):
    query = select(Bid).where(Bid.auction_id == auction_id).order_by(Bid.amount.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    bids = result.scalars().all()

    return list(bids)


@router.get("/winning")
async def get_winning_bids(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Bid).where(
            and_(
                Bid.buyer_id == current_user.id,
                Bid.is_winning == True
            )
        )
    )
    winning_bids = result.scalars().all()

    return {"winning_bids": list(winning_bids)}