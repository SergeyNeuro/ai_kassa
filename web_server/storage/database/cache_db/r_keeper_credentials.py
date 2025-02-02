"""storage/database/cache_db/r_keeper_credentials"""
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


class RKeeperCredentialsDbCache(database.BaseRKeeperCredentials, CommonCacheDb):
    cache = get_cache_obj(key=config.CACHE_NAME)
    db = DbChoicer(db_name=config.DB_TYPE).choice_r_keeper_credentials_obj()

    async def get_data_by_id(self, node_id: int) -> Union[
        db_schemas.r_keeper_credentials.RKeeperCredentialsSchem, None]:
        """Интерфейсный метод извлечения данных по первичному ключу
        Args:
            node_id: идентификатор записи (PK)
        """
        data = await self.search_in_cache_or_db_and_save(
            key=f"r_creds_menu_id:{node_id}",
            db_func=self.db.get_data_by_id,
            schema=db_schemas.r_keeper_credentials.RKeeperCredentialsSchem,
            live_time=60,
            args=(node_id,)
        )
        return data

    async def get_data_by_menu_id(self, menu_id: int) -> Union[
        db_schemas.r_keeper_credentials.RKeeperCredentialsSchem, None]:
        """Извлекаем креденшиалс по внешнему ключу - идентификатору меню
        Args:
            menu_id: идентификатор меню (FK)
        """
        data = await self.search_in_cache_or_db_and_save(
            key=f"r_creds_menu:{menu_id}",
            db_func=self.db.get_data_by_menu_id,
            schema=db_schemas.r_keeper_credentials.RKeeperCredentialsSchem,
            live_time=60,
            args=(menu_id,)
        )
        return data