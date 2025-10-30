from enum import Enum as PyEnum
from datetime import datetime
from app.db.database import Base
from sqlalchemy import Integer, String, Enum, DateTime, DECIMAL, Text, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from typing import Optional, List
from passlib.hash import bcrypt



class StatusChoices(str, PyEnum):
    admin = 'admin'
    seller = 'seller'
    buyer = 'buyer'


class StatusAuctionChoices(str, PyEnum):
    active = 'active'
    finished = 'finished'
    canceled = 'canceled'


class UserProfile(Base):
    __tablename__ = 'userprofile'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    user_name: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[StatusChoices] = mapped_column(Enum(StatusChoices), default=StatusChoices.buyer)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    password: Mapped[str] = mapped_column(String, nullable=False)

    buyer_bid: Mapped[List['Bid']] = relationship('Bid', back_populates='buyer',
                                                  cascade='all, delete-orphan')

    buyer_feedback: Mapped[List['Feedback']] = relationship('Feedback', back_populates='buyer',
                                                            foreign_keys='Feedback.buyer_id',
                                                            cascade='all, delete-orphan')
    seller_feedback: Mapped[List['Feedback']] = relationship('Feedback', back_populates='seller',
                                                             foreign_keys='Feedback.seller_id',
                                                             cascade='all, delete-orphan')
    user_token: Mapped[List['RefreshToken']] = relationship('RefreshToken', back_populates='user',
                                                            cascade='all, delete-orphan')

    def set_passwords(self, password: str):
        self.password = bcrypt.hash(password)

class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))
    user: Mapped[UserProfile] = relationship(UserProfile, back_populates='user_token')
    token: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Brand(Base):
    __tablename__ = 'brands'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    brand_name: Mapped[str] = mapped_column(String(32))
    brand_model: Mapped[List['Model']] = relationship('Model', back_populates='brand',
                                                      cascade='all, delete-orphan')
    brand_car: Mapped[List['Car']] = relationship('Car', back_populates='brand',
                                                  cascade='all, delete-orphan')


class Model(Base):
    __tablename__ = 'models'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    model_name: Mapped[str] = mapped_column(String(32))
    brand_id: Mapped[int] = mapped_column(ForeignKey('brands.id'))
    brand: Mapped[Brand] = relationship(Brand, back_populates='brand_model')
    model_car: Mapped[List['Car']] = relationship('Car', back_populates='model',
                                                  cascade='all, delete-orphan')


class Car(Base):
    __tablename__ = 'cars'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    year: Mapped[int] = mapped_column(Integer)
    fuel_type: Mapped[str] = mapped_column(String(24))
    transmission: Mapped[str] = mapped_column(String(32))
    mileage: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2))
    description: Mapped[str] = mapped_column(Text)
    seller: Mapped[StatusChoices] = mapped_column(Enum(StatusChoices), default=StatusChoices.buyer)

    brand_id: Mapped[int] = mapped_column(ForeignKey('brands.id'))
    brand: Mapped[Brand] = relationship(Brand, back_populates='brand_car')

    model_id: Mapped[int] = mapped_column(ForeignKey('models.id'))
    model: Mapped[Model] = relationship(Model, back_populates='model_car')

    car_images: Mapped[List['CarImage']] = relationship('CarImage', back_populates='car',
                                                        cascade='all, delete-orphan')
    car_auction: Mapped[List['Auction']] = relationship('Auction', back_populates='car',
                                                        cascade='all, delete-orphan')


class CarImage(Base):
    __tablename__ = 'car_images'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    car_image: Mapped[str] = mapped_column(String, nullable=True)
    car_id: Mapped[int] = mapped_column(ForeignKey('cars.id'))
    car: Mapped[Car] = relationship(Car, back_populates='car_images')


class Auction(Base):
    __tablename__ = 'auctions'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    start_price: Mapped[float] = mapped_column(DECIMAL(10, 2))
    status: Mapped[StatusAuctionChoices] = mapped_column(Enum(StatusAuctionChoices),
                                                         default=StatusAuctionChoices.active)
    min_price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=True, default=0.0)
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    car_id: Mapped[int] = mapped_column(ForeignKey('cars.id'), nullable=True)

    car: Mapped[Car] = relationship(Car, back_populates='car_auction')

    auction_bid: Mapped[List['Bid']] = relationship('Bid', back_populates='auction',
                                                    cascade='all, delete-orphan')


class Bid(Base):
    __tablename__ = 'bids'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2))
    created_add: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    auction_id: Mapped[int] = mapped_column(ForeignKey('auctions.id'))
    auction: Mapped[Auction] = relationship(Auction, back_populates='auction_bid')

    buyer_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))
    buyer: Mapped[UserProfile] = relationship(UserProfile, back_populates='buyer_bid')


class Feedback(Base):
    __tablename__ = 'feedbacks'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comment: Mapped[str] = mapped_column(String)
    created_add: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    buyer_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))
    buyer: Mapped[UserProfile] = relationship(UserProfile, back_populates='buyer_feedback',
                                              foreign_keys=[buyer_id])

    seller_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))
    seller: Mapped[UserProfile] = relationship(UserProfile, back_populates='seller_feedback',
                                               foreign_keys=[seller_id])