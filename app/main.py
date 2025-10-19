"""
Головний модуль застосунку FastAPI.

У цьому модулі створюється основний об'єкт FastAPI, налаштовуються:
- маршрути (auth, contacts),
- CORS-доступ,
- обмеження швидкості запитів (rate limiting),
- ініціалізація бази даних (SQLAlchemy),
- обробка помилок перевищення ліміту запитів.

Модуль є точкою входу для всього REST API застосунку.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import JSONResponse
from app.rate_limit.rate_limit import limiter
from app.database.database import Base, engine
from app.routes import auth, contacts

# ✅ Створюємо всі таблиці бази даних, якщо вони ще не існують
def init_db():
    Base.metadata.create_all(bind=engine)

# ✅ Ініціалізація FastAPI
app = FastAPI(title="Contacts API with Auth & Verification")

# ✅ Налаштування CORS
origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ✅ Налаштування rate limiting (SlowAPI)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Обробник виключення при перевищенні ліміту запитів.

    Args:
        request (Request): Поточний HTTP-запит.
        exc (RateLimitExceeded): Об'єкт винятку з деталями перевищення ліміту.

    Returns:
        JSONResponse: Відповідь із кодом 429 ("Too Many Requests").
    """
    return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})

# ✅ Підключення основних маршрутів застосунку
app.include_router(auth.router)
app.include_router(contacts.router)

@app.on_event("startup")
def on_startup():
    # Створюємо таблиці при запуску контейнера
    init_db()
   
