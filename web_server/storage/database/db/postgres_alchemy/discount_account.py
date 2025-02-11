"""storage/database/db/postgres_alchemy/models/discount_account"""

import logging
from datetime import datetime

from sqlalchemy import String, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from .alchemy_core import Base
from storage.base_interface import database


logger = logging.getLogger(__name__)


class DiscountAccountTable(Base):
    """ Таблица с данными скидочных аккаунтов
    Attr:
        id: уникальный идентификатор заказчика
        discount_id: идентификатор карточки или другого, что однозначно идентифицирует покупателя в системе
        phone: номер телефона покупателя
        email: почта покупателя
        type: тип обработки скидочной системы (1 - столовая 67)
        customer_id: идентификатор заказчика к которому относится данный покупатель
        created_at: дата создания записи
        update_at: дата обновления записи
        balance: баланс покупателя
    """
    __tablename__ = "discount_account_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    discount_id: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(12), nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    type: Mapped[int] = mapped_column(nullable=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers_table.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    update_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.utcnow)
    balance: Mapped[int] = mapped_column(default=0)


class DiscountAccountDAL(database.BaseDiscountAccount):
    pass