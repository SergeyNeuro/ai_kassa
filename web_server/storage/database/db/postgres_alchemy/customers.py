"""storage/database/db/postgres_alchemy/models/customer
Данные по аутентификации
"""
import logging
from typing import Optional

from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column

from .alchemy_core import Base, async_session_maker
from storage.base_interface import database
from schemas import db_schemas

logger = logging.getLogger(__name__)


class CustomersTable(Base):
    """ Таблица для всех заказчиков независимо от мессенджера
    Attr:
        id: уникальный идентификатор заказчика
        name: имя заказчика (опционально)
        phone: номер телефона заказчика
        email: почта заказчика
        login: логин для получения счета по токенам
        password: пароль для получения счета по токенам
    """
    __tablename__ = "customers_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(40))
    phone: Mapped[str] = mapped_column(String(12), nullable=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)
    password: Mapped[str] = mapped_column(String(20), nullable=True)
    discount_type: Mapped[int] = mapped_column(nullable=True)


class CustomersDAL(database.BaseCustomer):
    async def get_data_by_email(self, email: str) -> Optional[db_schemas.customer.CustomersSchem]:
        """Извлечение данных заказчика по email
        """
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    query = select(CustomersTable).where(CustomersTable.email == email)
                    res = await session.execute(query)
                    data = res.fetchone()
                    if data is not None:
                        return db_schemas.customer.CustomersSchem.model_validate(data[0], from_attributes=True)
        except Exception as _ex:
            logger.error(f"Ошибка при извлечении данных customer по email: {email} -> {_ex}")