"""storage/database/postgres_alchemy/food_point"""
from datetime import datetime
from typing import Union
import logging

from sqlalchemy import text, select, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .alchemy_core import Base, async_session_maker
from storage.base_interface import database

from schemas import db_schemas


logger = logging.getLogger(f"app.{__name__}")


class FoodPointTable(Base):
    """Таблица с данными о меню
    Attr:
        id: идентификатор записи
        name: название меню
        details: описание меню
        ai_model_name: наименование модели нейросети
        customer_id: идентификатор заказчика к которому меню относится
    """

    __tablename__ = "food_point_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    country: Mapped[str] = mapped_column(nullable=False)
    district: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers_table.id", ondelete="SET NULL"), nullable=False)