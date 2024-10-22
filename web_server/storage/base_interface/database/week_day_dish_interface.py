from abc import ABC, abstractmethod
from typing import Union, List


from schemas import db_schemas


class BaseWeekDayDish(ABC):
    """Интерфейсный класс работы с данными меню, которое зависит от дня недели"""
    @abstractmethod
    async def get_dish_list_by_week_day_and_changing_id(
            self,
            changing_id: int,
            week_day: int
    ) -> Union[db_schemas.dish.DishListSchem, None]:
        """Извлечение списка блюд зависимых от дня недели
        Args:
            changing_id: идентификатор сомневающейся позиции
            week_day: день недели за который нужно извлечь позиции
        """
        pass