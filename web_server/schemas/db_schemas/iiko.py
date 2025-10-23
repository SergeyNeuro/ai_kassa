
import datetime
from typing import Optional

from pydantic import BaseModel


class IikoCredentialsSchem(BaseModel):
    """Модель для валидации данных из таблицы креденшиалс iiko
    Attr:
        id: идентификатор записи
        name: наименование записи
        menu_id: идентификатор меню
        api_key: ключ по которому проходит авторизация
        created_at: дата создания
        update_at: дата изменения
    """
    id: int
    name: str
    menu_id: int
    aki_key: str
    organization_id: Optional[str]
    iiko_menu_id: Optional[str]
    created_at: datetime.datetime
    update_at: datetime.datetime


class IikoTerminalsSchem(BaseModel):
    """Модель для валидации данных терминалов iiko
    Attr:
        id: идентификатор записи
        terminal_id: идентификатор терминала в системе IIko
        kassa_id: идентификатор кассы рядом с которой установлен терминал
        created_at: дата создания
        update_at: дата изменения
    """
    id: int
    terminal_id: str
    kassa_id: int
    created_at: datetime.datetime
    update_at: datetime.datetime


class IikoDishSchem(BaseModel):
    """Модель для валидации данных блюд iiko
    Attr:
        id: идентификатор записи
        dish_id: идентификатор блюда из нашей системы
        created_at: дата создания
        update_at: дата изменения
    """
    id: int
    dish_id: int
    iiko_id: str
    created_at: datetime.datetime
    update_at: datetime.datetime