from app.db.models import (Car, Auction, Brand, Bid, Feedback, Model, UserProfile)
from sqladmin import ModelView


class UserProfileAdmin(ModelView, model=UserProfile):
    column_list = [UserProfile.user_name, UserProfile.status]


class CarAdmin(ModelView, model=Car):
    column_list = [Car.car_auction, Car.car_images]
