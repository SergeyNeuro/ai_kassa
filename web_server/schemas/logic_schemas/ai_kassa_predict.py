"""schemas/db_schem/ai_kassa_predict
Схемы связанные с аутентификацией
"""

import datetime
from typing import Union

from pydantic import BaseModel


class AiKassaPredictSchem(BaseModel):
    """Модель для валидации данных входящих
    при распознавании блюд на фото
    """
    timestamp: int
    menu_id: int