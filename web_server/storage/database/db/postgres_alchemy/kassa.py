"""storage/database/postgres_alchemy/kassa"""
from datetime import datetime
from typing import Union
import logging

from sqlalchemy import text, select, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .alchemy_core import Base, async_session_maker
from storage.base_interface import database

from schemas import db_schemas


logger = logging.getLogger(f"app.{__name__}")


class KassaTable(Base):
    """Таблица с данными о меню
    Attr:
        id: идентификатор записи
        name: название меню
        login: логин для входа на кассу
        password: пароль для входа на кассу
        address: ip адрес на котором стоит касса
        food_point_id: идентификатор точки питания на котором установлена касса
    """

    __tablename__ = "kassa_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    login: Mapped[str] = mapped_column(nullable=True)
    password: Mapped[str] = mapped_column(nullable=True)
    address: Mapped[str] = mapped_column(nullable=False)
    food_point_id: Mapped[int] = mapped_column(ForeignKey("food_point_table.id", ondelete="SET NULL"), nullable=False)


class KassaDAL(database.BaseKassa):
    pass