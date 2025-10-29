from fastapi import APIRouter
from app.api.v1 import auth, user, cars, auctions, bids, feedback

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(cars.router, prefix="/cars", tags=["cars"])
api_router.include_router(auctions.router, prefix="/auctions", tags=["auctions"])
api_router.include_router(bids.router, prefix="/bids", tags=["bids"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])