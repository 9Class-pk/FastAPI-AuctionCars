from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.car import Car
from app.models.auction import Auction, AuctionStatus
from app.models.bid import Bid
from app.schema.auction import AuctionCreate, AuctionResponse, AuctionListResponse, AuctionUpdate
from app.schema.bid import BidResponse
from app.core.security import oauth2_scheme, verify_token
from app.api.v1.auth import get_current_user
from app.services.websocket import websocket_manager

router = APIRouter()


@router.get("/", response_model=AuctionListResponse)
async def get_auctions(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        status: Optional[AuctionStatus] = None,
        active_only: bool = Query(False),
        db: AsyncSession = Depends(get_db)
):
    query = select(Auction).join(Car)

    if status:
        query = query.where(Auction.status == status)

    if active_only:
        query = query.where(
            and_(
                Auction.status == AuctionStatus.ACTIVE,
                Auction.end_time > datetime.utcnow()
            )
        )

    # Get total count
    from sqlalchemy import func
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    # Get paginated results
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    auctions = result.scalars().all()

    return AuctionListResponse(
        count=total,
        next=f"?skip={skip + limit}&limit={limit}" if skip + limit < total else None,
        previous=f"?skip={max(0, skip - limit)}&limit={limit}" if skip > 0 else None,
        results=list(auctions)
    )


@router.post("/", response_model=AuctionResponse)
async def create_auction(
        auction_data: AuctionCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.SELLER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can create auctions"
        )

    # Check if car exists and belongs to user
    result = await db.execute(
        select(Car).where(
            and_(
                Car.id == auction_data.car_id,
                Car.seller_id == current_user.id
            )
        )
    )
    car = result.scalar_one_or_none()

    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found or you don't have permission to create auction for this car"
        )

    # Check if car is approved
    if not car.is_approved and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Car must be approved by admin before creating auction"
        )

    # Create auction
    auction = Auction(
        **auction_data.dict(),
        current_price=auction_data.start_price,
        status=AuctionStatus.PENDING
    )

    db.add(auction)
    await db.commit()
    await db.refresh(auction)

    return auction


@router.get("/{auction_id}", response_model=AuctionResponse)
async def get_auction(auction_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Auction).where(Auction.id == auction_id)
    )
    auction = result.scalar_one_or_none()

    if not auction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auction not found"
        )

    return auction


@router.post("/{auction_id}/start")
async def start_auction(
        auction_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can start auctions"
        )

    result = await db.execute(select(Auction).where(Auction.id == auction_id))
    auction = result.scalar_one_or_none()

    if not auction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auction not found"
        )

    if auction.status != AuctionStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Auction can only be started from pending status"
        )

    auction.status = AuctionStatus.ACTIVE
    auction.start_time = datetime.utcnow()

    await db.commit()

    # Notify via WebSocket
    await websocket_manager.broadcast_to_auction(
        auction_id,
        {"type": "auction_started", "auction_id": auction_id}
    )

    return {"message": "Auction started successfully"}


@router.post("/{auction_id}/complete")
async def complete_auction(
        auction_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Auction).where(Auction.id == auction_id))
    auction = result.scalar_one_or_none()

    if not auction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auction not found"
        )

    # Check permissions
    if current_user.role != UserRole.ADMIN and auction.car.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    auction.status = AuctionStatus.COMPLETED
    auction.end_time = datetime.utcnow()

    # Find winning bid
    bid_result = await db.execute(
        select(Bid).where(
            and_(
                Bid.auction_id == auction_id,
                Bid.is_winning == True
            )
        )
    )
    winning_bid = bid_result.scalar_one_or_none()

    await db.commit()

    # Notify via WebSocket
    await websocket_manager.broadcast_to_auction(
        auction_id,
        {
            "type": "auction_completed",
            "auction_id": auction_id,
            "winning_bid": winning_bid.amount if winning_bid else None,
            "winner_id": winning_bid.buyer_id if winning_bid else None
        }
    )

    return {"message": "Auction completed successfully"}


@router.get("/{auction_id}/bids", response_model=List[BidResponse])
async def get_auction_bids(
        auction_id: int,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Bid).where(Bid.auction_id == auction_id).order_by(Bid.amount.desc())
    )
    bids = result.scalars().all()

    return list(bids)


@router.websocket("/{auction_id}/ws")
async def auction_websocket(websocket: WebSocket, auction_id: int):
    await websocket_manager.connect(websocket, auction_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle real-time messages if needed
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, auction_id)