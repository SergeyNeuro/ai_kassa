from abc import ABC, abstractmethod
from typing import Union


from schemas import db_schemas


class BaseRKeeperDish(ABC):
    """Интерфейсный класс работы с блюдами r-keeper"""
    @abstractmethod
    async def get_data_by_dish_id(self, dish_id: int) -> Union[db_schemas.r_keeper_dish.RKeeperDishSchem, None]:
        """Интерфейсный метод извлечения данных по внешнему ключу блюда
        Args:
            dish_id: идентификатор блюда из системы (FK)
        """
        pass