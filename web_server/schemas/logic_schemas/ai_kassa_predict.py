"""schemas/db_schem/ai_kassa_predict
Схемы связанные с аутентификацией
"""

import datetime
from typing import List, Optional

from pydantic import BaseModel


class AiKassaPredictSchem(BaseModel):
    """Модель для валидации данных входящих
    при распознавании блюд на фото
    """
    timestamp: int
    menu_id: int


class OneDishConfirmSchem(BaseModel):
    id: int
    name: str
    menu_id: int
    code_name: str
    type: int
    count_type: int
    count: int
    price: int
    changing_dish_id: Optional[int] = None


class ConfirmSchem(BaseModel):
    dish_data: OneDishConfirmSchem
    x1: Optional[int] = None
    y1: Optional[int] = None
    x2: Optional[int] = None
    y2: Optional[int] = None


class TestConfirmSchem(BaseModel):
    data: List[ConfirmSchem]
