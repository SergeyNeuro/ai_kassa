"""storage/database/postgres_alchemy/iiko_terminals"""
from datetime import datetime
from typing import Union
import logging

from sqlalchemy import text, select, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .alchemy_core import Base, async_session_maker
from storage.base_interface import database

from schemas import db_schemas


logger = logging.getLogger(f"app.{__name__}")


class IikoTerminalsTable(Base):
    """Таблица с данными терминалов системе IIKO
    Attr:
        id: идентификатор записи
        terminal_id: идентификатор терминала в системе IIko
        kassa_id: идентификатор кассы рядом с которой установлен терминал
        created_at: дата создания
        update_at: дата изменения
    """

    __tablename__ = "iiko_terminals_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    terminal_id: Mapped[str] = mapped_column(unique=True)
    kassa_id: Mapped[int] = mapped_column(ForeignKey("kassa_table.id", ondelete="CASCADE"), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    update_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.utcnow)


class IikoTerminalsDAL(database.BaseIikoTerminals):
    async def get_data_by_kassa_id(self, kassa_id: int) -> Union[db_schemas.iiko.IikoTerminalsSchem, None]:
        """Извлекаем данные терминала iiko по кассе к которой он относится
        Args:
            kassa_id: идентификатор кассы (FK)
        """
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    query = select(IikoTerminalsTable).where(IikoTerminalsTable.kassa_id == kassa_id)
                    res = await session.execute(query)
                    data = res.fetchone()
                    if data is not None:
                        return db_schemas.iiko.IikoTerminalsSchem.model_validate(data[0], from_attributes=True)
        except Exception as _ex:
            logger.error(f"Ошибка при извлечении данных iiko терминала по kassa_id: {kassa_id} -> {_ex}")