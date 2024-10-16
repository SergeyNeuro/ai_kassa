"""storage/database/postgres_alchemy/menu"""
from datetime import datetime
from typing import Union
import logging

from sqlalchemy import text, select, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .alchemy_core import Base, async_session_maker
from storage.base_interface import database

from schemas import db_schemas


logger = logging.getLogger(f"app.{__name__}")


class MenuTable(Base):
    """Таблица с данными о меню
    Attr:
        id: идентификатор записи
        name: название меню
        details: описание меню
        ai_model_name: наименование модели нейросети
        customer_id: идентификатор заказчика к которому меню относится
    """

    __tablename__ = "menu_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    details: Mapped[str] = mapped_column(nullable=True)
    ai_model_name: Mapped[str] = mapped_column(nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers_table.id", ondelete="SET NULL"), nullable=False)


class MenuDAL(database.BaseMenu):
    """Класс для получения данных меню"""

    async def get_data_by_id(self, node_id: int) -> Union[db_schemas.menu.MenuSchem, None]:
        """Интерфейсный метод извлечения данных по первичному ключу
        Args:
            node_id: идентификатор записи (PK)
        """
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    query = select(MenuTable).where(MenuTable.id == node_id)
                    res = await session.execute(query)
                    data = res.fetchone()
                    if data is not None:
                        return db_schemas.menu.MenuSchem.model_validate(data[0], from_attributes=True)
        except Exception as _ex:
            logger.error(f"Ошибка при извлечении данных меню по id: {node_id} -> {_ex}")