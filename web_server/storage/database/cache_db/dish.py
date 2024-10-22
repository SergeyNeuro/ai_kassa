"""storage/database/cache_db/dish"""
from typing import Union, List
import logging

# импортируем абстрактные интерфейсы
from storage.base_interface import database

# импортируем необходимые схемы
from schemas import db_schemas

# импортируем глобальные переменные
import config

# импортируем объекты для взаимодействия
from .common import CommonCacheDb
from storage.database.cache.cache_choicer import get_cache_obj
from storage.database.db.db_choicer import DbChoicer

logger = logging.getLogger(f"app.{__name__}")


class DishDbCache(database.BaseDish, CommonCacheDb):
    cache = get_cache_obj(key=config.CACHE_NAME)
    db = DbChoicer(db_name=config.DB_TYPE).choice_dish_obj()

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
        return await self.db.get_data_by_menu_and_code_names(
            menu_id=menu_id, code_names=code_names
        )

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
        return await self.db.add_new_dish(
            name=name,
            menu_id=menu_id,
            code_name=code_name,
            type=type,
            count_type=count_type,
            count=count,
            price=price,
            changing_dish_id=changing_dish_id
        )

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
        data = await self.search_in_cache_or_db_and_save(
            key=f"menu:{menu_id}:code_name:{code_name}",
            db_func=self.db.get_data_by_menu_and_code_name,
            schema=db_schemas.dish.DishSchem,
            live_time=60,
            args=(menu_id, code_name, )
        )
        logger.debug(f"Извлек данные меню -> {data}")
        return data

    async def get_data_by_changing_id(self, changing_id: int) -> Union[db_schemas.dish.DishListSchem, None]:
        """Извлечение списка блюд по внешнему ключу ссылки на сомневающееся блюдо
        Args:
            changing_id: (FK) идентификатор сомнительного блюда
        """
        data = await self.search_in_cache_or_db_and_save(
            key=f"dish_changing_id:{changing_id}",
            db_func=self.db.get_data_by_changing_id,
            schema=db_schemas.dish.DishListSchem,
            live_time=60,
            args=(changing_id,)
        )
        return data