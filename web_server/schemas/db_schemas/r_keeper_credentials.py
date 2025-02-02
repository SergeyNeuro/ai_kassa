
import datetime
from typing import Union

from pydantic import BaseModel


class RKeeperCredentialsSchem(BaseModel):
    """Модель для валидации данных из таблицы креденшиалс r_keeper
    Attr:
        id - идентификатор записи
        menu_id: идентификатор меню, к которому относится запись
        name: наиенование записи
        token: токен авторизации в системе r_keeper
        object_id: идентификатор объекта к которому относится запрос
        create_at: дата создавния записи
        update_at: дата обновления записи
    """
    id: int
    menu_id: int
    name: str
    token: str
    object_id: int
    created_at: datetime.datetime
    update_at: datetime.datetime
