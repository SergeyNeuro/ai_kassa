"""storage/database/postgres_alchemy/iiko_dishes"""
from datetime import datetime
from typing import Union
import logging

from sqlalchemy import text, select, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .alchemy_core import Base, async_session_maker
from storage.base_interface import database

from schemas import db_schemas


logger = logging.getLogger(f"app.{__name__}")


class IikoDishesTable(Base):
    """Таблица с данным блюд из системы iiko
    Attr:
        id: идентификатор записи
        dish_id: идентификатор блюда из нашей системы
        created_at: дата создания
        update_at: дата изменения
    """

    __tablename__ = "iiko_dishes_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dish_table.id", ondelete="CASCADE"), unique=True)
    iiko_id: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    update_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.utcnow)


class IikoDishesDAL(database.BaseIikoDishes):
    async def get_data_by_dish_id(self, dish_id: int) -> Union[db_schemas.iiko.IikoDishSchem, None]:
        """Извлекаем данные блюда iiko по блюду из нашей системы к которой он относится
        Args:
            dish_id: идентификатор блюда (FK)
        """
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    query = select(IikoDishesTable).where(IikoDishesTable.dish_id == dish_id)
                    res = await session.execute(query)
                    data = res.fetchone()
                    if data is not None:
                        return db_schemas.iiko.IikoDishSchem.model_validate(data[0], from_attributes=True)
        except Exception as _ex:
            logger.error(f"Ошибка при извлечении данных iiko по dish_id: {dish_id} -> {_ex}")