"""storage/database/cache_db/customers"""
from typing import Optional
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


class KassaDbCache(database.BaseKassa, CommonCacheDb):
    cache = get_cache_obj(key=config.CACHE_NAME)
    db = DbChoicer(db_name=config.DB_TYPE).choice_kassa_obj()

    async def get_data_by_id(self, node_id: int) -> Optional[db_schemas.kassa.KassaSchem]:
        """Извлекаем данные по ID"""
        pass
        data = await self.search_in_cache_or_db_and_save(
            key=f"kassa:id:{node_id}",
            db_func=self.db.get_data_by_id,
            schema=db_schemas.kassa.KassaSchem,
            live_time=60,
            args=(node_id, )
        )
        logger.debug(f"Извлек данные kassa -> {data}")
        return data