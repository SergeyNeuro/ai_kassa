"""storage/database/postgres_alchemy/r_keeper_dish"""
from datetime import datetime
from typing import Union
import logging

from sqlalchemy import text, select, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .alchemy_core import Base, async_session_maker
from storage.base_interface import database

from schemas import db_schemas


logger = logging.getLogger(f"app.{__name__}")


class RKeeperDishTable(Base):
    """Таблица с данными о меню
    Attr:
        id: идентификатор записи
        name: название меню
        details: описание меню
        ai_model_name: наименование модели нейросети
        customer_id: идентификатор заказчика к которому меню относится
        system_name: наименование системы учета (например r_keeper)
    """

    __tablename__ = "r_keeper_dish_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dish_table.id", ondelete="CASCADE"), nullable=True, unique=True)
    name: Mapped[str] = mapped_column(nullable=False)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu_table.id", ondelete="CASCADE"), nullable=True)


class RKeeperDishDAL(database.BaseRKeeperDish):

    async def get_data_by_dish_id(self, dish_id: int) -> Union[db_schemas.r_keeper_dish.RKeeperDishSchem, None]:
        """Интерфейсный метод извлечения данных по внешнему ключу блюда
        Args:
            dish_id: идентификатор блюда из системы (FK)
        """
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    query = select(RKeeperDishTable).where(RKeeperDishTable.dish_id == dish_id)
                    res = await session.execute(query)
                    data = res.fetchone()
                    if data is not None:
                        return db_schemas.r_keeper_dish.RKeeperDishSchem.model_validate(data[0], from_attributes=True)
        except Exception as _ex:
            logger.error(f"Ошибка при извлечении r_keeper блюда по dish_id: {dish_id} -> {_ex}")