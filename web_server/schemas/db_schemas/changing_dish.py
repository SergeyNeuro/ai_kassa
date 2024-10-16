import datetime
from typing import Union

from pydantic import BaseModel


class ChangingDishSchem(BaseModel):
    """Модель для валидации данных о блюдах, которые схожи между собой
    """
    id: int
    menu_id: int
    name: str
