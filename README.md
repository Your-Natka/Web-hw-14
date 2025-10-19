# Web-hw-14

app/
├── __init__.py
├── main.py                # головний файл (FastAPI app, middleware, routers)
├── database.py            # SQLAlchemy + get_db
├── models.py              # User, Contact
├── schemas.py             # Pydantic схеми
├── crud.py                # логіка бази (users, contacts)
├── mailer.py              # email (verification, reset)
├── cloudinary_utils.py    # завантаження аватарів
├── rate_limit.py          # SlowAPI rate limiter
├── redis_cache.py         # підключення Redis
└── routes/
    ├── auth.py            # маршрути авторизації
    └── contacts.py        # маршрути контактів


WEB-HW-14
├── Dockerfile                                   
├── README.md   
├── __pycache__                               
│ └── test_api.cpython-312-pytest-8.4.2 pyc    
├── app                                         
│ ├── README.md 
│ ├── __init__.py
│ ├── __pycache__ 
│ │ ├── __init__.cpython-312.pyc   
│ │ ├── __init__.cpython-313.pyc
│ │ ├── __init__.cpython-39.pyc
│ │ ├── auth.cpython-312.pyc
│ │ ├── auth.cpython-313.pyc
│ │ ├── cloudinary_utils.cpython-312.pyc
│ │ ├── cloudinary_utils.cpython-313.pyc
│ │ ├── config.cpython-312.pyc
│ │ ├── crud.cpython-312.pyc
│ │ ├── crud.cpython-313.pyc
│ │ ├── crud.cpython-39.pyc
│ │ ├── database.cpython-312.pyc
│ │ ├── database.cpython-313.pyc
│ │ ├── database.cpython-39.pyc
│ │ ├── mailer.cpython-312.pyc 
│ │ ├── mailer.cpython-313.pyc
│ │ ├── main.cpython-312.pyc 
│ │ ├── main.cpython-313.pyc 
│ │ ├── main.cpython-39.pyc
│ │ ├── models.cpython-312.pyc
│ │ ├── models.cpython-313.pyc 
│ │ ├── models.cpython-39.pyc  
│ │ ├── rate_limit.cpython-313.pyc  
│ │ ├── redis_cache.cpython-312.pyc 
│ │ ├── redis_cache.cpython-313.pyc
│ │ ├── schemas.cpython-312.pyc  
│ │ ├── schemas.cpython-313.pyc 
│ │ └── schemas.cpython-39.pyc 
│ ├── cloudinary_utils.py  
│ ├── config.py
│ ├── crud.py  
│ ├── database   
│ │ └── __pycache__ 
│ ├── database.py 
│ ├── mailer.py 
│ ├── main.py
│ ├── models.py  
│ ├── rate_limit.py  
│ ├── redis_cache.py
│ ├── routes
│ │ ├── __init__.py 
│ │ ├── Auth   
│ │ ├── __pycache__  
│ │ ├── auth.py  
│ │ └── contacts.py  
│ ├── schemas.py  
│ └── utils.py 
├── docker-compose.yml   
├── docs 
│ ├── Makefile   
│ ├── _build
│ │ ├── doctrees 
│ │ └── html 
│ ├── app.rst   
│ ├── conf.py                                                                         
│ ├── index.rst 
│ ├── make.bat  
│ ├── modules.rst 
│ └── source    
│ ├── app.rst 
│ └── modules.rst 
├── poetry.lock 
├── pyproject.toml 
├── requirements.txt 
├── test
│ ├── __init__.py  
│ ├── __pycache__   
│ │ ├── __init__.cpython-312.pyc 
│ │ ├── test_functional_contacts.cpython-312-pytest-8.4.2.pyc  
│ │ ├── test_unit_repository_auth.cpython-312-pytest-8.4.2.pyc                        
│ │ └── test_unit_repository_contacts.cpython-312-pytest-8.4.2.pyc 
│ ├── test_functional_contacts.py          → функціональні тести
│ ├── test_unit_repository_auth.py         → модульні тести для auth 
│ └── test_unit_repository_contacts.py     → модульні тести для contacts  
├── test.db       
├── test_api.py 
└── test_avatar.png

Встановлюємо залежності:

pip install -r requirements.txt

Запускаємо Docker сервіси (Postgres + Redis):

docker-compose up -d

Запускаємо FastAPI сервер:

uvicorn app.main:app --reload

Потім відкрий у браузері:
👉 http://127.0.0.1:8000/docs

Запусти всі сервіси у фоні:
docker-compose up -d

Переконайся, що веб-контейнер працює:
docker ps

Тепер запусти тест:
docker exec -it web-hw-14-web-1 python3 test_api.py

Після цього пересоби контейнер:
docker-compose up --build -d

Тепер запусти тест:
docker-compose exec web pytest --cov=app