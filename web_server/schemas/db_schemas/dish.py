import datetime
from typing import List, Optional

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
    count: Optional[int]
    price: int
    changing_dish_id: Optional[int]
    barcode: Optional[str]


class DishListSchem(BaseModel):
    dish_list: List[DishSchem]