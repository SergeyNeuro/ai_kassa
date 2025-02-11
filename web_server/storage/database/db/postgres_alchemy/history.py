"""storage/database/postgres_alchemy/history"""
from datetime import datetime
from typing import Union
import logging

from sqlalchemy import text, select, ForeignKey, Column, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .alchemy_core import Base, async_session_maker
from storage.base_interface import database

from schemas import db_schemas


logger = logging.getLogger(f"app.{__name__}")


class HistoryTable(Base):
    """Таблица с данными истории покупок через кассу
    Attr:
        id: идентификатор записи
        products: JSON с данными что именно и в каком кол-вы было куплено на кассе
        value: сумма на которую была сделана покупка
        kassa_id: идентификатор кассы с который была сделана покупка
        created_at: дата и время покупки
    """

    __tablename__ = "history_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    products = Column(JSON, nullable=False)
    value: Mapped[int] = mapped_column(nullable=False)
    kassa_id: Mapped[int] = mapped_column(ForeignKey("kassa_table.id", ondelete="SET NULL"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))


class HistoryDAL(database.BaseHistory):
    pass