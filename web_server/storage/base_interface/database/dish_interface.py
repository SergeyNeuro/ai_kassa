from abc import ABC, abstractmethod
from typing import Union, List


from schemas import db_schemas


class BaseDish(ABC):
    """Интерфейсный класс работы с данными с блюдами"""
    @abstractmethod
    async def get_data_by_menu_and_code_names(
            self,
            menu_id: int,
            code_names: list
    ) -> Union[List[db_schemas.dish.DishSchem], None]:
        """Извлечения списка блюд по кодовым названиям и идентификатору меню
        к которому они относятся
        Args:
            menu_id: (FK) идентификатор меню
            code_names: список кодовых имен блюд
        """
        pass

    @abstractmethod
    async def add_new_dish(
            self,
            name: str,
            menu_id: int,
            code_name: str,
            type: int,
            count_type: int,
            count: Union[int, None],
            price: int,
            changing_dish_id: Union[int, None]
    ) -> Union[db_schemas.dish.DishSchem, None]:
        """Добавления нового блюда в БД
        Args:
            name: наименования блюда
            menu_id: (FK) идентификатор меню к которому относится блюдо
            code_name: кодовое имя блюда (которое идентифицирует нейросеть)
            type: тип блюда
                (
                    1 - салат
                    2 - суп
                    3 - гарнир
                    4 - овощное блюдо
                    5 - рыбное блюдо
                    6 - блюдо из птицы
                    7 - блюдо из мяса
                    8 - выпечка
                    9 - напиток
                    10 - добавки
                    11 - неопределенное
                )
            count_type: тип количественной оценки блюда
                (
                    1 - измеряется в порциях
                    2 - измеряется в штуках
                    3 - измеряется в массе
                    4 - измеряется в объеме
                )
            count: единица кол-ва блюда
            price: стоимость единицы блюда
            changing_dish_id: (FK) сомнительная позиция, которую можно спутать с другой
        """
        pass

    @abstractmethod
    async def get_data_by_menu_and_code_name(
            self,
            menu_id: int,
            code_name: str
    ) -> Union[db_schemas.dish.DishSchem, None]:
        """Извлечение одного блюда из БД
        Args:
            menu_id: (FK) идентификатор меню к которому относится блюдо
            code_name: кодовое имя блюда
        """
        pass