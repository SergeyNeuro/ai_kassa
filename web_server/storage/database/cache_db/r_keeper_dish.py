"""storage/database/cache_db/r_keeper_dish"""
from calendar import month
from typing import Union
import logging

# импортируем абстрактные интерфесы
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


class RKeeperDishDbCache(database.BaseRKeeperDish, CommonCacheDb):
    cache = get_cache_obj(key=config.CACHE_NAME)
    db = DbChoicer(db_name=config.DB_TYPE).choice_r_keeper_dish_obj()

    async def get_data_by_dish_id(self, dish_id: int) -> Union[db_schemas.r_keeper_dish.RKeeperDishSchem, None]:
        """Интерфейсный метод извлечения данных по внешнему ключу блюда
        Args:
            dish_id: идентификатор блюда из системы (FK)
        """
        data = await self.search_in_cache_or_db_and_save(
            key=f"r_dish:{dish_id}",
            db_func=self.db.get_data_by_dish_id,
            schema=db_schemas.r_keeper_dish.RKeeperDishSchem,
            live_time=60,
            args=(dish_id,)
        )
        return data