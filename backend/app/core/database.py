from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Укажите URL для подключения к БД
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:12345@localhost:5432/marki")

# Создайте движок для подключения к БД
engine = create_engine(
    DATABASE_URL
)

# Создайте фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()