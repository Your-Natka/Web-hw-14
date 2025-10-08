"""
Модуль CRUD-операцій для користувачів і контактів.

Містить функції для створення, читання, оновлення та видалення (Create, Read, Update, Delete)
даних у базі даних через SQLAlchemy ORM.

Також містить допоміжні функції для хешування паролів і перевірки автентичності.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.context import CryptContext
from app import models, schemas

# Контекст для хешування паролів
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------- Users ----------
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Отримати користувача за email.

    Args:
        db (Session): Сесія бази даних SQLAlchemy.
        email (str): Електронна пошта користувача.

    Returns:
        Optional[User]: Об’єкт користувача або None, якщо не знайдено.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """
    Отримати користувача за ID.

    Args:
        db (Session): Сесія бази даних SQLAlchemy.
        user_id (int): Ідентифікатор користувача.

    Returns:
        Optional[User]: Об’єкт користувача або None, якщо не знайдено.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_password_hash(password: str) -> str:
    """
    Хешує пароль користувача за допомогою bcrypt.

    Args:
        password (str): Звичайний пароль.

    Returns:
        str: Хешований пароль.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Перевіряє правильність пароля користувача.

    Args:
        plain_password (str): Звичайний (нехешований) пароль.
        hashed_password (str): Хешований пароль із бази даних.

    Returns:
        bool: True, якщо пароль вірний, інакше False.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, email: str, hashed_password: str, username: Optional[str] = None) -> models.User:
    """
    Створює нового користувача в базі даних.

    Args:
        db (Session): Сесія бази даних.
        email (str): Електронна пошта користувача.
        hashed_password (str): Хешований пароль.
        username (Optional[str]): Ім’я користувача (необов’язкове).

    Returns:
        User: Створений об’єкт користувача.
    """
    db_user = models.User(email=email, password=hashed_password[:72], username=username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user: models.User, new_password: str) -> models.User:
    """
    Оновлює пароль користувача.

    Args:
        db (Session): Сесія бази даних.
        user (User): Об’єкт користувача.
        new_password (str): Новий пароль (нехешований).

    Returns:
        User: Оновлений користувач.
    """
    user.password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user

def update_user_avatar(db: Session, user: models.User, avatar_url: str) -> models.User:
    """
    Оновлює URL аватара користувача.

    Args:
        db (Session): Сесія бази даних.
        user (User): Поточний користувач.
        avatar_url (str): Нове посилання на аватар.

    Returns:
        User: Оновлений користувач.
    """
    user.avatar_url = avatar_url
    db.commit()
    db.refresh(user)
    return user

def verify_user_email(db: Session, user: models.User) -> models.User:
    """
    Позначає користувача як верифікованого.

    Args:
        db (Session): Сесія бази даних.
        user (User): Об’єкт користувача.

    Returns:
        User: Оновлений користувач зі статусом `is_verified=True`.
    """
    user.is_verified = True
    db.commit()
    db.refresh(user)
    return user

# ---------- Contacts ----------

def create_contact(db: Session, contact_in: schemas.ContactCreate, user_id: int) -> models.Contact:
    """
    Створює новий контакт для користувача.

    Args:
        db (Session): Сесія бази даних.
        contact_in (ContactCreate): Дані нового контакту.
        user_id (int): Ідентифікатор власника контакту.

    Returns:
        Contact: Створений контакт.
    """
    db_contact = models.Contact(**contact_in.dict(), owner_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts(db: Session, user_id: int) -> List[models.Contact]:
    """
    Отримує всі контакти користувача.

    Args:
        db (Session): Сесія бази даних.
        user_id (int): Ідентифікатор користувача.

    Returns:
        List[Contact]: Список контактів.
    """
    return db.query(models.Contact).filter(models.Contact.owner_id == user_id).all()

def get_contact(db: Session, contact_id: int, user_id: int) -> Optional[models.Contact]:
    """
    Отримує один контакт користувача за ID.

    Args:
        db (Session): Сесія бази даних.
        contact_id (int): Ідентифікатор контакту.
        user_id (int): Ідентифікатор користувача-власника.

    Returns:
        Optional[Contact]: Об’єкт контакту або None, якщо не знайдено.
    """
    return db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.owner_id == user_id
    ).first()

def update_contact(db: Session, contact: models.Contact, updates: schemas.ContactUpdate) -> models.Contact:
    """
    Оновлює дані контакту.

    Args:
        db (Session): Сесія бази даних.
        contact (Contact): Поточний контакт.
        updates (ContactUpdate): Об’єкт зі зміненими даними.

    Returns:
        Contact: Оновлений контакт.
    """
    for k, v in updates.dict(exclude_unset=True).items():
        setattr(contact, k, v)
    db.commit()
    db.refresh(contact)
    return contact

def delete_contact(db: Session, contact: models.Contact) -> None:
    """
    Видаляє контакт із бази даних.

    Args:
        db (Session): Сесія бази даних.
        contact (Contact): Контакт, який потрібно видалити.

    Returns:
        None
    """
    db.delete(contact)
    db.commit()