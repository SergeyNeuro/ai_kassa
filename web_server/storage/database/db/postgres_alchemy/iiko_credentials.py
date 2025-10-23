"""storage/database/postgres_alchemy/iiko_credentials"""
from datetime import datetime
from typing import Union
import logging

from sqlalchemy import text, select, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .alchemy_core import Base, async_session_maker
from storage.base_interface import database

from schemas import db_schemas


logger = logging.getLogger(f"app.{__name__}")


class IikoCredentialsTable(Base):
    """Таблица с авторизационными данными в системе IIKO
    Attr:
        id: идентификатор записи
        name: наименование записи
        menu_id: идентификатор меню
        api_key: ключ по которому проходит авторизация
        created_at: дата создания
        update_at: дата изменения
    """

    __tablename__ = "iiko_credentials_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu_table.id", ondelete="CASCADE"), nullable=False, unique=True)
    aki_key: Mapped[str] = mapped_column(nullable=False)
    organization_id: Mapped[str] = mapped_column(nullable=True)
    iiko_menu_id: Mapped[str] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    update_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.utcnow)


class IikoCredentialsDAL(database.BaseIikoCredentials):
    async def get_data_by_menu_id(self, menu_id: int) -> Union[
        db_schemas.iiko.IikoCredentialsSchem, None]:
        """Извлекаем credentials по внешнему ключу - идентификатору меню
        Args:
            menu_id: идентификатор меню (FK)
        """
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    query = select(IikoCredentialsTable).where(IikoCredentialsTable.menu_id == menu_id)
                    res = await session.execute(query)
                    data = res.fetchone()
                    if data is not None:
                        return db_schemas.iiko.IikoCredentialsSchem.model_validate(data[0], from_attributes=True)
        except Exception as _ex:
            logger.error(f"Ошибка при извлечении данных iiko по menu_id: {menu_id} -> {_ex}")

