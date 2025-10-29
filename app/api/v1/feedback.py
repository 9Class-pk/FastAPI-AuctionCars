from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select, and_, func

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.feedback import Feedback
from app.models.bid import Bid
from app.models.auction import Auction, AuctionStatus
from app.schema.feedback import FeedbackCreate, FeedbackResponse, FeedbackListResponse
from app.api.v1.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=FeedbackResponse)
async def create_feedback(
        feedback_data: FeedbackCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Check if buyer has won any auctions from this seller
    result = await db.execute(
        select(Bid).join(Auction).join(Bid.auction).where(
            and_(
                Bid.buyer_id == current_user.id,
                Bid.is_winning == True,
                Auction.status == AuctionStatus.COMPLETED,
                Auction.car.has(seller_id=feedback_data.seller_id)
            )
        )
    )
    winning_bid = result.scalar_one_or_none()

    if not winning_bid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only leave feedback for sellers you have won auctions from"
        )

    # Check if feedback already exists for this transaction
    existing_feedback = await db.execute(
        select(Feedback).where(
            and_(
                Feedback.buyer_id == current_user.id,
                Feedback.seller_id == feedback_data.seller_id,
                Feedback.id == winning_bid.id  # Using bid id as transaction reference
            )
        )
    )

    if existing_feedback.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already left feedback for this transaction"
        )

    # Check rating is valid
    if feedback_data.rating < 1 or feedback_data.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )

    # Create feedback
    feedback = Feedback(
        **feedback_data.dict(),
        buyer_id=current_user.id
    )

    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    return feedback


@router.get("/seller/{seller_id}", response_model=FeedbackListResponse)
async def get_seller_feedback(
        seller_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_db)
):
    # Check if seller exists
    result = await db.execute(select(User).where(User.id == seller_id))
    seller = result.scalar_one_or_none()

    if not seller or seller.role != UserRole.SELLER:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found"
        )

    # Get feedback with buyer info
    from sqlalchemy.orm import selectinload
    query = select(Feedback).where(Feedback.seller_id == seller_id).options(
        selectinload(Feedback.buyer)
    ).order_by(Feedback.created_at.desc())

    # Get total count
    count_result = await db.execute(
        select(func.count()).where(Feedback.seller_id == seller_id)
    )
    total = count_result.scalar_one()

    # Get paginated results
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    feedbacks = result.scalars().all()

    # Calculate average rating
    avg_rating_result = await db.execute(
        select(func.avg(Feedback.rating)).where(Feedback.seller_id == seller_id)
    )
    avg_rating = avg_rating_result.scalar_one() or 0

    return FeedbackListResponse(
        count=total,
        average_rating=round(avg_rating, 2),
        next=f"?skip={skip + limit}&limit={limit}" if skip + limit < total else None,
        previous=f"?skip={max(0, skip - limit)}&limit={limit}" if skip > 0 else None,
        results=list(feedbacks)
    )


@router.get("/my-feedback", response_model=List[FeedbackResponse])
async def get_my_feedback(
        as_seller: bool = Query(False),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if as_seller and current_user.role == UserRole.SELLER:
        # Get feedback received as seller
        query = select(Feedback).where(Feedback.seller_id == current_user.id)
    else:
        # Get feedback given as buyer
        query = select(Feedback).where(Feedback.buyer_id == current_user.id)

    query = query.order_by(Feedback.created_at.desc())
    result = await db.execute(query)
    feedbacks = result.scalars().all()

    return list(feedbacks)


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
        feedback_id: int,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Feedback).where(Feedback.id == feedback_id))
    feedback = result.scalar_one_or_none()

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )

    return feedback


@router.delete("/{feedback_id}")
async def delete_feedback(
        feedback_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Feedback).where(Feedback.id == feedback_id))
    feedback = result.scalar_one_or_none()

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )

    # Only buyer who created feedback or admin can delete
    if feedback.buyer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    await db.delete(feedback)
    await db.commit()

    return {"message": "Feedback deleted successfully"}