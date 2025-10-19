"""
Модуль керування контактами користувачів.

Цей модуль містить маршрути для CRUD-операцій над контактами:
створення, перегляд, оновлення, видалення контактів, а також
завантаження аватарів користувачів.

Використовується FastAPI, SQLAlchemy, Cloudinary для зберігання зображень
та Redis (через rate limiter) для обмеження запитів.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List
from app.crud import crud
from app.database.database import get_db
from app.models import models
from app.routes.auth import get_current_user
from app.rate_limit.rate_limit import limiter
from app.cloudinary_utils.cloudinary_utils import upload_avatar_file
from app.schemas import schemas

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/ping")
def ping():
    """
    Перевірка працездатності сервісу контактів.

    Returns:
        dict: Повідомлення з підтвердженням роботи.
    """
    return {"message": "Contacts OK"}

@router.get("/", response_model=List[schemas.ContactOut])
def list_contacts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Отримує список контактів для поточного користувача.

    Args:
        db (Session): Сесія бази даних.
        current_user (models.User): Поточний авторизований користувач.

    Returns:
        List[schemas.ContactOut]: Список об’єктів контактів користувача.
    """
    return crud.get_contacts(db, current_user.id)


# ✅ Єдиний правильний POST-ендпоінт
@router.post("/", response_model=schemas.ContactOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_contact(
    request: Request,  # 🔹 обов’язково потрібно для slowapi
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Створює новий контакт для поточного користувача.

    Args:
        request (Request): Об’єкт запиту (використовується для ліміту запитів).
        contact (schemas.ContactCreate): Дані нового контакту.
        db (Session): Сесія бази даних.
        current_user (models.User): Поточний користувач.

    Returns:
        schemas.ContactOut: Створений контакт.

    Raises:
        HTTPException: Якщо перевищено ліміт запитів.
    """
    return crud.create_contact(db, contact, current_user.id)


@router.put("/{contact_id}", response_model=schemas.ContactOut)
def update_contact(
    contact_id: int,
    updates: schemas.ContactUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Оновлює дані існуючого контакту користувача.

    Args:
        contact_id (int): Ідентифікатор контакту.
        updates (schemas.ContactUpdate): Дані для оновлення.
        db (Session): Сесія бази даних.
        current_user (models.User): Поточний користувач.

    Returns:
        schemas.ContactOut: Оновлений контакт.

    Raises:
        HTTPException: Якщо контакт не знайдено.
    """
    contact = crud.get_contact(db, contact_id, current_user.id)
    if not contact:
        raise HTTPException(status_code=404, detail="Not found")
    return crud.update_contact(db, contact, updates)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Видаляє контакт користувача.

    Args:
        contact_id (int): Ідентифікатор контакту.
        db (Session): Сесія бази даних.
        current_user (models.User): Поточний користувач.

    Returns:
        None: Якщо контакт успішно видалено.

    Raises:
        HTTPException: Якщо контакт не знайдено.
    """
    contact = crud.get_contact(db, contact_id, current_user.id)
    if not contact:
        raise HTTPException(status_code=404, detail="Not found")
    crud.delete_contact(db, contact)
    return None


@router.put("/{contact_id}/avatar", status_code=status.HTTP_200_OK)
def upload_avatar(
    contact_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Завантажує аватар користувача у Cloudinary
    та оновлює URL аватару в базі даних.

    Args:
        file (UploadFile): Файл зображення, який завантажується.
        db (Session): Сесія бази даних.
        current_user (models.User): Поточний користувач.

    Returns:
        dict: Посилання на завантажений аватар.
    """
    url = upload_avatar_file(file.file)
    crud.update_user_avatar(db, current_user, url)
    return {"avatar_url": url}
