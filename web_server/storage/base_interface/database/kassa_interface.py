from abc import ABC
from typing import Optional

from schemas import db_schemas


class BaseKassa(ABC):
    """Интерфейс класс для взаимодействия данными касс"""
    async def get_data_by_id(self, node_id: int) -> Optional[db_schemas.kassa.KassaSchem]:
        """Извлекаем данные по ID"""
        pass