from typing import Union

from pydantic import BaseModel


class WeekDayDishSchem(BaseModel):
    """Модель для валидации данных по блюдам,
    которые подаются в определенные дни недели
    """
    id: int
    week_day: int
    dish_id: int
    changing_dish_id: int