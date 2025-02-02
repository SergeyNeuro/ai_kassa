
import datetime
from typing import Union

from pydantic import BaseModel


class RKeeperDishSchem(BaseModel):
    """Модель для валидации данных из таблицы блюд r_keeper
    и их привязке к блюдам из БД нашей системы
    Attr:
        id - идентификатор записи
        dish_id: идентификатор блюда из нашей системы
        menu_id: идентификатор меню из нашей системы
        name: наименование блюда из системы r-keeper
        r_keeper_id: идентификатор блюда из системы r-keeper

    """
    id: int
    dish_id: int
    name: str
    r_keeper_id: int
    menu_id: int