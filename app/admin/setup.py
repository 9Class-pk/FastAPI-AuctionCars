from .views import (UserProfileAdmin, CarAdmin)

from fastapi import FastAPI
from sqladmin import Admin
from app.db.database import engine

def setup_admin(store_app: FastAPI):
    admin = Admin(store_app, engine)
    admin.add_view(UserProfileAdmin)
    admin.add_view(CarAdmin)