"""storage/database/cache_db/weeK-day_dish"""
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


class WeekDayDishDbCache(database.BaseWeekDayDish, CommonCacheDb):
    cache = get_cache_obj(key=config.CACHE_NAME)
    db = DbChoicer(db_name=config.DB_TYPE).choice_week_day_dish_obj()

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
        data = await self.search_in_cache_or_db_and_save(
            key=f"week_day:{week_day}:changing_id:{changing_id}",
            db_func=self.db.get_dish_list_by_week_day_and_changing_id,
            schema=db_schemas.dish.DishListSchem,
            live_time=60,
            args=(changing_id, week_day,)
        )
        return data