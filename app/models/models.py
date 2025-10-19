"""
Модуль моделей бази даних.

Містить ORM-моделі SQLAlchemy для таблиць:
- User (користувачі)
- Contact (контакти користувачів)

Використовується SQLAlchemy ORM та базовий клас Base із модуля app.database.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime

class User(Base):
    """
    Модель користувача системи.

    Зберігає дані про користувачів: електронну пошту, пароль, ім’я користувача,
    стан верифікації, URL аватара та час створення облікового запису.

    Attributes:
        id (int): Первинний ключ користувача.
        email (str): Унікальна електронна пошта.
        password (str): Хешований пароль користувача.
        username (str): Унікальне ім’я користувача (необов’язкове поле).
        is_verified (bool): Статус верифікації користувача.
        avatar_url (str): Посилання на зображення аватара.
        created_at (datetime): Час створення користувача.
        contacts (relationship): Зв’язок один-до-багатьох з моделлю Contact.
    """
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # храним хеш
    username = Column(String(50), unique=True, index=True, nullable=True)
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    contacts = relationship("Contact", back_populates="owner", cascade="all, delete-orphan")


class Contact(Base):
    """
    Модель контакту користувача.

    Використовується для зберігання контактної інформації користувача:
    ім’я, email, телефон, адреса та зв’язок із власником (User).

    Attributes:
        id (int): Первинний ключ контакту.
        name (str): Ім’я контакту.
        email (str): Електронна пошта контакту.
        phone (str): Телефонний номер контакту.
        address (str): Адреса контакту.
        owner_id (int): Зовнішній ключ до таблиці користувачів (users.id).
        owner (relationship): Зв’язок із користувачем (User).
    """
    
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="contacts")