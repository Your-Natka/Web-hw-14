"""
Модуль аутентифікації користувачів.

Цей модуль містить маршрути та логіку для:
- реєстрації користувачів;
- входу в систему (отримання JWT-токена);
- підтвердження електронної пошти;
- скидання та зміни пароля.

Використовується FastAPI, SQLAlchemy, Redis для кешування,
JWT для токенів доступу, та Mailhog (через send_email)
для тестування email-повідомлень.
"""

from datetime import datetime, timedelta
from typing import Optional
import os, jwt
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from urllib.parse import unquote
from app.database import get_db
from app import crud, models, schemas
from app.mailer import send_verification_email, send_reset_email
from app.redis_cache import redis_client

# Завантаження змінних середовища
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REDIS_TTL = int(os.getenv("REDIS_TTL", 3600))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
router = APIRouter(prefix="/auth", tags=["auth"])

def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Створює JWT-токен для користувача.

    Args:
        data (dict): Дані, які потрібно закодувати (наприклад, email користувача).
        expires_delta (Optional[timedelta]): Час життя токена. Якщо не вказано — береться зі змінних середовища.

    Returns:
        str: Згенерований JWT-токен.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    """
    Розшифровує JWT-токен та повертає дані.

    Args:
        token (str): Рядок токена.

    Returns:
        dict: Розкодовані дані з токена.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Аутентифікація користувача за email та паролем.

    Використовується стандартна схема OAuth2PasswordRequestForm.
    Якщо авторизація успішна — генерується JWT-токен.

    Args:
        form_data (OAuth2PasswordRequestForm): Дані користувача (email, пароль).
        db (Session): Сесія бази даних.

    Returns:
        dict: Об'єкт із токеном доступу (`access_token`) та типом токена (`bearer`).

    Raises:
        HTTPException: Якщо облікові дані некоректні.
    """
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_token({"sub": user.email})
    # Кешування користувача у Redis
    try:
        redis_client.set(f"user:{user.id}", user.email, ex=REDIS_TTL)
    except Exception:
        pass
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """
    Отримує поточного користувача за JWT-токеном.

    Args:
        token (str): JWT-токен із заголовку `Authorization`.
        db (Session): Сесія бази даних.

    Returns:
        models.User: Об'єкт користувача з бази даних.

    Raises:
        HTTPException: Якщо токен недійсний, прострочений або користувача не знайдено.
    """
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Реєстрація нового користувача.

    Створює нового користувача, хешує пароль та надсилає лист
    із підтвердженням на email.

    Args:
        user_in (schemas.UserCreate): Дані нового користувача.
        db (Session): Сесія бази даних.

    Returns:
        schemas.UserOut: Створений користувач.

    Raises:
        HTTPException: Якщо користувач уже існує.
    """
    if crud.get_user_by_email(db, email=user_in.email):
        raise HTTPException(status_code=400, detail="User already exists")
    hashed = crud.get_password_hash(user_in.password) if hasattr(crud, "get_password_hash") else crud.get_password_hash(user_in.password)
    # створити підпис користувача очікує хешований пароль
    new_user = crud.create_user(db, email=user_in.email, hashed_password=hashed) if "hashed_password" in crud.create_user.__code__.co_varnames else crud.create_user(db, email=user_in.email, hashed_password=hashed)  # fallback
    # отже, використовуйте нашого створеного користувача: почта, пароль, ім'я.
    # Якщо підпис вашого crud.create_user відрізняється, відкоригуйте відповідно
    # надіслати лист для підтвердження
    token = create_token({"sub": new_user.email, "type": "verify"}, expires_delta=timedelta(hours=1))
    send_verification_email(new_user.email, token)
    return new_user

@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Підтвердження електронної пошти користувача.

    Args:
        token (str): JWT-токен із посилання підтвердження.
        db (Session): Сесія бази даних.

    Returns:
        dict: Повідомлення про успішну верифікацію.

    Raises:
        HTTPException: Якщо токен недійсний, прострочений або користувач не знайдений.
    """
    token = unquote(token)
    try:
        payload = decode_token(token)
        if payload.get("type") != "verify":
            raise HTTPException(status_code=400, detail="Invalid token type")
        email = payload.get("sub")
        user = crud.get_user_by_email(db, email=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        crud.verify_user_email(db, user)
        return {"message": "Email verified"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

@router.post("/forgot-password")
def forgot_password(data: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Запит на скидання пароля.

    Користувач вводить свій email, система надсилає лист
    із посиланням для зміни пароля.

    Args:
        data (schemas.PasswordResetRequest): Email користувача.
        db (Session): Сесія бази даних.

    Returns:
        dict: Повідомлення про успішну відправку листа.
    """
    user = crud.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = create_token({"sub": user.email, "type": "reset"}, expires_delta=timedelta(hours=1))
    send_reset_email(user.email, token)
    return {"message": "Password reset email sent"}

@router.post("/reset-password")
def reset_password(data: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    """
    Оновлення пароля користувача після запиту на скидання.

    Args:
        data (schemas.PasswordResetConfirm): Новий пароль і токен підтвердження.
        db (Session): Сесія бази даних.

    Returns:
        dict: Повідомлення про успішну зміну пароля.

    Raises:
        HTTPException: Якщо токен недійсний або користувач не знайдений.
    """
    try:
        payload = decode_token(data.token)
        if payload.get("type") != "reset":
            raise HTTPException(status_code=400, detail="Invalid token type")
        email = payload.get("sub")
        user = crud.get_user_by_email(db, email=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        crud.update_user_password(db, user, data.new_password)
        return {"message": "Password updated"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid token")