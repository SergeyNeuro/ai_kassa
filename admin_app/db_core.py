from sqlalchemy import create_engine, URL
from sqlalchemy.ext.declarative import declarative_base

from config import DB_HOST, DB_NAME, DB_PORT, DB_PASS, DB_USER

# Создаем URL для подключения к БД
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=5432,
    database=DB_NAME,
)

# Создаем базовый класс, от которого будут наследоваться все модели
Base = declarative_base()

# Создаем движок
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
)