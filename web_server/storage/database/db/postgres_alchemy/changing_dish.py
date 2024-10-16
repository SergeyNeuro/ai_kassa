"""storage/database/postgres_alchemy/changing_dish"""
from datetime import datetime
from typing import Union
import logging

from sqlalchemy import text, select, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .alchemy_core import Base, async_session_maker
from storage.base_interface import database

from schemas import db_schemas


logger = logging.getLogger(f"app.{__name__}")


class ChangingDishTable(Base):
    """Таблица с данными о меню
    Attr:
        id: идентификатор записи
        name: название позиции
        menu_id: идентификатор меню, к которому относится запись
    """

    __tablename__ = "changing_dish_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu_table.id", ondelete="SET NULL"), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)


class ChangingDishDAL(database.BaseChangingDish):
    """Класс для получения данных меню"""

    async def get_data_by_id(self, node_id: int) -> Union[db_schemas.changing_dish.ChangingDishSchem, None]:
        """Интерфейсный метод извлечения данных по первичному ключу
        Args:
            node_id: идентификатор записи (PK)
        """
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    query = select(ChangingDishTable).where(ChangingDishTable.id == node_id)
                    res = await session.execute(query)
                    data = res.fetchone()
                    if data is not None:
                        return db_schemas.changing_dish.ChangingDishSchem.model_validate(data[0], from_attributes=True)
        except Exception as _ex:
            logger.error(f"Ошибка при извлечении данных меню по id: {node_id} -> {_ex}")