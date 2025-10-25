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


class CustomersDbCache(database.BaseCustomer, CommonCacheDb):
    cache = get_cache_obj(key=config.CACHE_NAME)
    db = DbChoicer(db_name=config.DB_TYPE).choice_customers_obj()

    async def get_data_by_email(self, email: str) -> Optional[db_schemas.customer.CustomersSchem]:
        """Извлечение данных заказчика по email
        """
        data = await self.search_in_cache_or_db_and_save(
            key=f"customer:email:{email}",
            db_func=self.db.get_data_by_email,
            schema=db_schemas.customer.CustomersSchem,
            live_time=60,
            args=(email, )
        )
        logger.debug(f"Извлек данные customer -> {data}")
        return data