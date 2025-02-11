"""storage/database/db/postgres_alchemy/models/discount_transaction"""

import logging
from datetime import datetime

from sqlalchemy import String, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from .alchemy_core import Base
from storage.base_interface import database


logger = logging.getLogger(__name__)


class DiscountTransactionTable(Base):
    """ Таблица с данными транзакций по пополнению/трате баллов
    Attr:
        id: уникальный идентификатор заказчика
        way: путь транзакции (1 - трата, 2 - пополнение)
        value: кол-во баллов
        history_id: транзакция по покупке по которой были потрачены/пополнены баллы
        created_at: дата создания записи
    """
    __tablename__ = "discount_transaction_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    way: Mapped[int] = mapped_column(nullable=False)
    value: Mapped[int] = mapped_column(nullable=False)
    history_id: Mapped[int] = mapped_column(ForeignKey("history_table.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))


class DiscountTransactionDAL(database.BaseDiscountTransaction):
    pass