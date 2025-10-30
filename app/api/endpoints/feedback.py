from fastapi import HTTPException, Depends, APIRouter
from app.db.models import Feedback
from app.db.schemas import FeedbackSchema
from app.db.database import SessionLocal
from sqlalchemy.orm import Session
from typing import List


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

feedback_router = APIRouter(
    prefix='/feedback',
    tags=['Feedback']
)


@feedback_router.post('/create/', response_model=FeedbackSchema)
async def create_feedback(feedback: FeedbackSchema, db: Session = Depends(get_db)):
    feedback_db = Feedback(
        rating=feedback.rating,
        comment=feedback.comment,
        created_add=feedback.created_add,
        buyer_id=feedback.buyer_id,
        seller_id=feedback.seller_id,
    )
    db.add(feedback_db)
    db.commit()
    db.refresh(feedback_db)
    return feedback_db



@feedback_router.get('/list/', response_model=List[FeedbackSchema])
async def last_feedback(db: Session = Depends(get_db)):
   return db.query(Feedback).all()