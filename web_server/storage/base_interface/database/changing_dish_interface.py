from abc import ABC, abstractmethod
from typing import Union


from schemas import db_schemas


class BaseChangingDish(ABC):
    """Интерфейсный класс работы с данными меню"""
    @abstractmethod
    async def get_data_by_id(self, node_id: int) -> Union[db_schemas.changing_dish.ChangingDishSchem, None]:
        """Интерфейсный метод извлечения данных по первичному ключу
        Args:
            node_id: идентификатор записи (PK)
        """
        pass