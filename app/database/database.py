"""
Модуль `database.py`

Забезпечує конфігурацію бази даних для всього застосунку:
створення двигуна SQLAlchemy, фабрики сесій та базового класу моделей.

Цей модуль є центральним місцем для підключення до бази даних,
ініціалізації ORM (Object Relational Mapping) та отримання сесії бази даних
через залежності FastAPI.

Передбачено використання PostgreSQL за замовчуванням, але можна вказати
інший URL бази даних через змінну середовища `DATABASE_URL`.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

# ---------- Конфігурація бази даних ----------

#: URL підключення до бази даних. Може бути перевизначено через змінну середовища.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/postgres")

#: SQLAlchemy engine — створює з’єднання з базою даних.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

#: Фабрика сесій, що створює об’єкти Session для взаємодії з базою даних.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#: Базовий клас для всіх ORM-моделей.
Base = declarative_base()

def get_db():
    """
    Отримує об’єкт сесії бази даних для запитів у FastAPI.

    Ця функція є генератором-залежністю для FastAPI.  
    Вона створює нову сесію бази даних перед виконанням запиту
    і гарантує її закриття після завершення.

    Yields:
        Session: Активна сесія бази даних SQLAlchemy.

    Example:
        Використання у FastAPI маршруті:
        ```python
        from fastapi import Depends
        from .database import get_db

        @router.get("/users/")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
        ```
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()