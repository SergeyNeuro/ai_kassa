import datetime
from typing import Union

from pydantic import BaseModel


class DishSchem(BaseModel):
    """Модель для валидации данных конкретного блюда
    """
    id: int
    name: str
    menu_id: int
    code_name: str
    type: int
    count_type: int
    count: Union[int, None]
    price: int
    changing_dish_id: Union[int, None]
