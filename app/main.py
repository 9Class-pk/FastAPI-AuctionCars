import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import  SessionLocal
from sqlalchemy.orm import Session
from typing import List
from app.api.endpoints import (auctions, auth, bids, brands,
                               cars, feedback, models, users, social_auth)
from app.admin.setup import setup_admin
import os
from fastapi.staticfiles import StaticFiles
from app import static
from starlette.middleware.sessions import SessionMiddleware
from app.middlewares.middleware import LoggingMiddleware



async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





auction = FastAPI()



auction.include_router(users.user_router)
auction.include_router(cars.car_router)
auction.include_router(auctions.auction_router)
auction.include_router(bids.bid_router)
auction.include_router(brands.brand_router)
auction.include_router(feedback.feedback_router)
auction.include_router(models.model_router)
auction.include_router(social_auth.social_router)

setup_admin(auction)




#oauth middlewares
auction.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")
auction.add_middleware(LoggingMiddleware)





#StaticFiles for images////////////
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

auction.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
#Product/////////
from fastapi.responses import HTMLResponse

@auction.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>Store</title>
        </head>
        <body>
            <h1>Salam Aleikum</h1>
            <p>Документация: <a href="/docs">Swagger</a></p>
        </body>
    </html>
    """




if __name__ == '__main__':
    uvicorn.run(auction, host='127.0.0.1', port=8001)


# Простейший API
