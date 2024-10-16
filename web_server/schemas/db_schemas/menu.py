
import datetime
from typing import Union

from pydantic import BaseModel


class MenuSchem(BaseModel):
    """Модель для валидации данных из таблицы меню
    Attr:
        id - идентификатор токена в системе
        name - наименование меню
        customer_id - идентификатор заказчика
        ai_model_name - наименование модели нейросети
        details - дополнительное описание меню
    """
    id: int
    name: str
    customer_id: int
    ai_model_name: str
    details: Union[str, None]