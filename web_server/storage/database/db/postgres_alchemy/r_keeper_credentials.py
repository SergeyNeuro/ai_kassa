"""storage/database/postgres_alchemy/r_keeper_credentials"""
from datetime import datetime
from typing import Union
import logging

from sqlalchemy import text, select, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .alchemy_core import Base, async_session_maker
from storage.base_interface import database

from schemas import db_schemas


logger = logging.getLogger(f"app.{__name__}")


class RKeeperCredentialsTable(Base):
    """Таблица с данными о меню
    Attr:
        id: идентификатор записи
        name: название меню
        details: описание меню
        ai_model_name: наименование модели нейросети
        customer_id: идентификатор заказчика к которому меню относится
        system_name: наименование системы учета (например r_keeper)
    """

    __tablename__ = "r_keeper_credentials_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu_table.id", ondelete="CASCADE"), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(nullable=False)
    token: Mapped[str] = mapped_column(nullable=False)
    object_id: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    update_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.utcnow)


class RKeeperCredentialsDAL(database.BaseRKeeperCredentials):

    async def get_data_by_id(self, node_id: int) -> Union[
        db_schemas.r_keeper_credentials.RKeeperCredentialsSchem, None]:
        """Интерфейсный метод извлечения данных по первичному ключу
        Args:
            node_id: идентификатор записи (PK)
        """
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    query = select(RKeeperCredentialsTable).where(RKeeperCredentialsTable.id == node_id)
                    res = await session.execute(query)
                    data = res.fetchone()
                    if data is not None:
                        return db_schemas.r_keeper_credentials.RKeeperCredentialsSchem.model_validate(data[0], from_attributes=True)
        except Exception as _ex:
            logger.error(f"Ошибка при извлечении данных r_keeper_credentials по ID: {node_id} -> {_ex}")

    async def get_data_by_menu_id(self, menu_id: int) -> Union[
        db_schemas.r_keeper_credentials.RKeeperCredentialsSchem, None]:
        """Извлекаем креденшиалс по внешнему ключу - идентификатору меню
        Args:
            menu_id: идентификатор меню (FK)
        """
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    query = select(RKeeperCredentialsTable).where(RKeeperCredentialsTable.menu_id == menu_id)
                    res = await session.execute(query)
                    data = res.fetchone()
                    if data is not None:
                        return db_schemas.r_keeper_credentials.RKeeperCredentialsSchem.model_validate(data[0], from_attributes=True)
        except Exception as _ex:
            logger.error(f"Ошибка при извлечении данных r_keeper_credentials по menu_id: {menu_id} -> {_ex}")

