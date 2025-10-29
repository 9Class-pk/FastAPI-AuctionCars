from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    auction_id = Column(Integer, ForeignKey("auctions.id"))
    buyer_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    is_winner = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    auction = relationship("Auction", back_populates="bids")
    buyer = relationship("User", back_populates="bids")

    def __repr__(self):
        return f"<Bid {self.amount} on Auction {self.auction_id}>"