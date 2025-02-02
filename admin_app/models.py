"""storage/database/db/postgres_alchemy/models/customer
Данные по аутентификации
"""
import logging
from datetime import datetime

from sqlalchemy import String, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import logging

from db_core import Base

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
    customer = relationship("CustomersTable")
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    update_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.utcnow)


class MenuTable(Base):
    """Таблица с данными о меню
    Attr:
        id: идентификатор записи
        name: название меню
        details: описание меню
        customer_id: идентификатор заказчика к которому меню относится
    """

    __tablename__ = "menu_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    ai_model_name: Mapped[str] = mapped_column(nullable=False)
    details: Mapped[str] = mapped_column(nullable=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers_table.id", ondelete="SET NULL"), nullable=False)
    system_name: Mapped[str] = mapped_column(nullable=False)
    customer = relationship("CustomersTable")


class ChangingDishTable(Base):
    """Таблица с данными о меню
    Attr:
        id: идентификатор записи
        name: название позиции
        menu_id: идентификатор меню, к которому относится запись
    """

    __tablename__ = "changing_dish_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu_table.id", ondelete="SET NULL"), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    strategy: Mapped[str] = mapped_column(default="all_dish")
    menu = relationship("MenuTable")


class DishTable(Base):
    """Таблица с данными о блюдах
    """

    __tablename__ = "dish_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu_table.id", ondelete="SET NULL"), nullable=False)
    code_name: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[int] = mapped_column(nullable=False)
    count_type: Mapped[int] = mapped_column(default=1)
    count: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)
    changing_dish_id: Mapped[int] = mapped_column(ForeignKey("changing_dish_table.id", ondelete="SET NULL"), nullable=True)
    menu = relationship("MenuTable")
    changing_dish = relationship("ChangingDishTable")


class FoodPointTable(Base):
    """Таблица с данными о меню
    Attr:
        id: идентификатор записи
        name: название меню
        details: описание меню
        ai_model_name: наименование модели нейросети
        customer_id: идентификатор заказчика к которому меню относится
    """

    __tablename__ = "food_point_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    country: Mapped[str] = mapped_column(nullable=False)
    district: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers_table.id", ondelete="SET NULL"), nullable=False)
    customer = relationship("CustomersTable")


class WeekDayDishTable(Base):
    """Таблица с данными о меню
    Attr:
        id: идентификатор записи
        week_day: день недели в integer представлении
        dish_id: идентификатор блюда
        changing_dish_id: идентификатор сомневающегося блюда
    """

    __tablename__ = "week_day_dish_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    week_day: Mapped[int] = mapped_column(nullable=False)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dish_table.id", ondelete="CASCADE"), nullable=False)
    changing_dish_id: Mapped[int] = mapped_column(ForeignKey("changing_dish_table.id", ondelete="CASCADE"),
                                                  nullable=False)
    dish = relationship("DishTable")
    changing_dish = relationship("ChangingDishTable")


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
    menu = relationship("MenuTable")


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
    dish = relationship("DishTable")
    name: Mapped[str] = mapped_column(nullable=False)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu_table.id", ondelete="CASCADE"), nullable=True)
    menu = relationship("MenuTable")