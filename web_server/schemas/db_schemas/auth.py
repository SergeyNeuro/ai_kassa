"""schemas/db_schem/auth
Схемы связанные с аутентификацией
"""

import datetime
from typing import Union

from pydantic import BaseModel


class AuthSchem(BaseModel):
    """Модель для валидации данных из таблицы
    по аутентификации
    Attr:
        id - идентификатор токена в системе
        token - значение токена доступа (именно это значение будет прилетать в запросе)
        name - название токена (для удобства опозначания)
        role - уровень доступа который дан данному токену (чем ниже, тем больше доступно)
        customer_id: идентификатор заказчика, к которому относится токен
        details - опциональное описание токена
        created_at - дата создания
        update_at - дата обновления
    """
    id: int
    token: str
    name: str
    role: int
    customer_id: Union[int, None]
    details: Union[str, None]
    created_at: datetime.datetime
    update_at: datetime.datetime