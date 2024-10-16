import datetime
from typing import Union

from pydantic import BaseModel


class FoodPointSchem(BaseModel):
    """Модель для валидации данных точки питания
    """
    id: int
    country: str
    district: str
    city: str
    address: str
    customer_id: int