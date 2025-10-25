from abc import ABC
from typing import Optional

from schemas import db_schemas


class BaseFoodPoint(ABC):
    """Интерфейс класс хранящий данные о точке питания"""
    async def get_data_by_id(self, node_id: int) -> Optional[db_schemas.food_point.FoodPointSchem]:
        """Извлечение данных по ID"""
        pass