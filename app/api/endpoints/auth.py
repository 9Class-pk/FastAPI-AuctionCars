from fastapi import HTTPException, Depends, APIRouter
from app.db.models import UserProfile, RefreshToken
from app.db.schemas import UserProfileOutSchema, UserProfileLoginSchema, UserProfileCreateSchema
from app.db.database import SessionLocal
from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.context import CryptContext
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from app.config import (ALGORITHM, SECRET_KEY,
                              ACCESS_TOKEN_LIFETIME,
                              REFRESH_TOKEN_LIFETIME)
from datetime import datetime, timedelta
from app.encryption import encrypt_data, decrypt_data


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

auth_router = APIRouter(prefix='/auth', tags=['Auth'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_LIFETIME))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_LIFETIME))



@auth_router.post('/register', response_model=dict)
async def register(user: UserProfileCreateSchema, db: Session = Depends(get_db)):
    # Проверка по имени пользователя
    if db.query(UserProfile).filter(UserProfile.user_name == user.user_name).first():
        raise HTTPException(status_code=400, detail="user_name уже существует")

    # Шифруем email и телефон
    encrypted_email = encrypt_data(user.email)
    encrypted_phone = encrypt_data(user.phone_number) if user.phone_number else None

    # Проверка по зашифрованному email
    if db.query(UserProfile).filter(UserProfile.email == encrypted_email).first():
        raise HTTPException(status_code=400, detail="email уже существует")

    # Хешируем пароль
    hash_password = get_password_hash(user.password)

    # Создаем пользователя с зашифрованными данными
    user_db = UserProfile(
        user_name=user.user_name,
        email=encrypted_email,
        age=user.age,
        phone_number=encrypted_phone,
        status=user.status,
        password=hash_password
    )
    db.add(user_db)
    db.commit()
    db.refresh(user_db)

    return {"message": "Вы успешно зарегистрировались", "user_id": user_db.id}


@auth_router.post('/login')
async def login(form_data: UserProfileLoginSchema = Depends(),
                db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.email == form_data.email).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail='Данные логина неправильные')

    access_token = create_access_token({"sub": user.user_name})
    refresh_token = create_refresh_token({"sub": user.user_name})

    new_token = RefreshToken(user_id=user.id, token=refresh_token)
    db.add(new_token)
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@auth_router.post('/logout')
async def logout(refresh_token: str, db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()

    if not stored_token:
        raise HTTPException(status_code=401, detail='Данные логина неправильные')

    db.add(stored_token)
    db.commit()
    return {"message": "Вы успешно вышли"}


@auth_router.post('/refresh')
async def refresh(refresh_token: str, db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not stored_token:
        raise HTTPException(status_code=401, detail='Данные логина неправильные')

    access_token = create_access_token({"sub": stored_token.id})
    return {"access_token": access_token, "token_type": "bearer"}