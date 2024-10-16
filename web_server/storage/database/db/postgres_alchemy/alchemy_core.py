"""
Через данный модуль осуществляется подключения к базе данных.
    Здесь находится единая точка входа в БД для всех частей веб приложения.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import URL
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import DB_USER, DB_PASS, DB_HOST, DB_NAME, DB_PORT

# Создаем ссылку для подключения к базе данных (через данную ссылку можно переподлючиться на удаленную БД)
database_url = URL.create(
    drivername="postgresql+asyncpg",
    username=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

# Создаем движок взаимодействия с базой данных. Движок асинхронный (asyncpg)
engine = create_async_engine(database_url, echo=False, pool_size=5, max_overflow=10)

# Создаем объект асинхронной сессии на движке для взаимодействия SqlAclhemy с БД
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Декларативный класс для создания на его основе своих таблиц моделей данных"""
    pass