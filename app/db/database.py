from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import select
from sqlalchemy.ext.declarative import declarative_base


DB_URL = 'postgresql://postgres:adminadmin@localhost/auction'
engine = create_engine(DB_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()