"""storage/database/postgres_alchemy/auth"""
from datetime import datetime
from typing import Union
import logging

from sqlalchemy import text, select, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .alchemy_core import Base, async_session_maker
from storage.base_interface import database

from schemas import db_schemas


logger = logging.getLogger(f"app.{__name__}")


class AuthTokenTable(Base):
    """Таблица в которой содержатся данные о токенах доступа для API
    id - идентификатор
    token - значение токена доступа (именно это значение будет прилетать в запросе)
    name - название токена (для удобства опозначания)
    role - уровень доступа который дан данному токену (чем ниже, тем больше доступно)
    details - опциональное описание токена
    created_at - дата создания
    update_at - дата обновления
    """

    __tablename__ = "auth_token_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(nullable=False, unique=True)
    name: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[int] = mapped_column(nullable=False)
    details: Mapped[str] = mapped_column(nullable=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers_table.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    update_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.utcnow)


class AuthDAL(database.BaseAuth):
    """Класс для получения данных аутентификации запроса"""

    async def get_data_by_token(self, token: str) -> Union[db_schemas.auth.AuthSchem, None]:
        """Данный метод извлекает данные аутентификации по токену
        Args:
            token: токен доступа, по которому осуществляется проверка
        """
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    query = select(AuthTokenTable).where(AuthTokenTable.token == token)
                    res = await session.execute(query)
                    data = res.fetchone()
                    if data is not None:
                        return db_schemas.auth.AuthSchem.model_validate(data[0], from_attributes=True)
        except Exception as _ex:
            logger.error(f"Ошибка при извлечении данных по токену: {token} -> {_ex}")
