"""storage/database/cache_db/auth"""
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


class MenuDbCache(database.BaseMenu, CommonCacheDb):
    cache = get_cache_obj(key=config.CACHE_NAME)
    db = DbChoicer(db_name=config.DB_TYPE).choice_menu_obj()

    async def get_data_by_id(self, node_id: int) -> Union[db_schemas.menu.MenuSchem, None]:
        """Интерфейсный метод извлечения данных по первичному ключу
        Args:
            node_id: идентификатор записи (PK)
        """
        logger.debug(f"Извлекаю данные меню по id: {node_id}")
        data = await self.search_in_cache_or_db_and_save(
            key=f"menu:{node_id}",
            db_func=self.db.get_data_by_id,
            schema=db_schemas.menu.MenuSchem,
            live_time=60,
            args=(node_id,)
        )
        logger.debug(f"Извлек данные меню -> {data}")
        return data