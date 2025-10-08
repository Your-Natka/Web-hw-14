"""
Модуль `schemas.py`

Містить Pydantic-схеми (DTO — Data Transfer Objects), які використовуються для
валідації, серіалізації та десеріалізації даних між клієнтом і сервером.

Класи описують структуру запитів і відповідей для користувачів та контактів.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ---------- Users ----------

class UserCreate(BaseModel):
    """
    Схема для створення нового користувача.

    Attributes:
        email (EmailStr): Електронна пошта користувача.
        password (str): Пароль у відкритому вигляді (буде хешовано).
        username (Optional[str]): Ім’я користувача (необов’язкове).
    """
    email: EmailStr
    password: str
    username: Optional[str] = None

class UserOut(BaseModel):
    """
    Схема для відображення даних користувача у відповідях API.

    Attributes:
        id (int): Унікальний ідентифікатор користувача.
        email (EmailStr): Електронна пошта користувача.
        username (Optional[str]): Ім’я користувача.
        is_verified (bool): Статус підтвердження електронної пошти.
        avatar_url (Optional[str]): Посилання на аватар користувача.
        created_at (datetime): Дата створення облікового запису.
    """
    id: int
    email: EmailStr
    username: Optional[str]
    is_verified: bool
    avatar_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class AvatarUpdate(BaseModel):
    """
    Схема для оновлення аватара користувача.

    Attributes:
        avatar_url (str): Посилання на новий аватар.
    """
    avatar_url: str

class EmailVerification(BaseModel):
    """
    Схема для перевірки електронної пошти користувача.

    Attributes:
        email (EmailStr): Електронна пошта користувача.
        token (str): Токен підтвердження електронної пошти.
    """
    email: EmailStr
    token: str

class PasswordResetRequest(BaseModel):
    """
    Схема для запиту відновлення пароля (етап 1).

    Attributes:
        email (EmailStr): Електронна пошта користувача для відправлення листа.
    """
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """
    Схема для підтвердження скидання пароля (етап 2).

    Attributes:
        token (str): Токен підтвердження.
        new_password (str): Новий пароль.
    """
    token: str
    new_password: str
    
# ---------- Contacts ----------

class ContactBase(BaseModel):
    """
    Базова схема для контактів (спільні поля для створення та оновлення).

    Attributes:
        name (str): Ім’я контакту.
        email (EmailStr): Електронна пошта контакту.
        phone (Optional[str]): Номер телефону (необов’язковий).
        address (Optional[str]): Адреса контакту (необов’язкова).
    """
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None

class ContactCreate(ContactBase):
    """
    Схема для створення нового контакту (успадковує базові поля).
    """
    pass

class ContactUpdate(BaseModel):
    """
    Схема для оновлення існуючого контакту.

    Усі поля необов’язкові, дозволяє часткове оновлення.

    Attributes:
        name (Optional[str]): Нове ім’я.
        email (Optional[EmailStr]): Нова електронна пошта.
        phone (Optional[str]): Новий номер телефону.
        address (Optional[str]): Нова адреса.
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class ContactOut(ContactBase):
    """
    Схема для повернення контактів користувачу у відповідях API.

    Attributes:
        id (int): Унікальний ідентифікатор контакту.
        owner_id (int): Ідентифікатор користувача-власника контакту.
    """
    id: int
    owner_id: int

    class Config:
        from_attributes = True
