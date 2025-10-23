"""storage/database/cache_db/iiko"""
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


class IikoCredentialsDbCache(database.BaseIikoCredentials, CommonCacheDb):
    cache = get_cache_obj(key=config.CACHE_NAME)
    db = DbChoicer(db_name=config.DB_TYPE).choice_iiko_credentials_obj()

    async def get_data_by_menu_id(self, menu_id: int) -> Union[
        db_schemas.iiko.IikoCredentialsSchem, None]:
        """Извлекаем креденшиалс по внешнему ключу - идентификатору меню
        Args:
            menu_id: идентификатор меню (FK)
        """
        data = await self.search_in_cache_or_db_and_save(
            key=f"iiko:menu:{menu_id}",
            db_func=self.db.get_data_by_menu_id,
            schema=db_schemas.iiko.IikoCredentialsSchem,
            live_time=60,
            args=(menu_id,)
        )
        return data


class IikoTerminalsDbCache(database.BaseIikoTerminals, CommonCacheDb):
    cache = get_cache_obj(key=config.CACHE_NAME)
    db = DbChoicer(db_name=config.DB_TYPE).choice_iiko_terminals_obj()

    async def get_data_by_kassa_id(self, kassa_id: int) -> Union[db_schemas.iiko.IikoTerminalsSchem, None]:
        """Извлекаем данные терминала iiko по кассе к которой он относится
        Args:
            kassa_id: идентификатор кассы (FK)
        """
        data = await self.search_in_cache_or_db_and_save(
            key=f"iiko_terminal:kassa:{kassa_id}",
            db_func=self.db.get_data_by_kassa_id,
            schema=db_schemas.iiko.IikoTerminalsSchem,
            live_time=60,
            args=(kassa_id,)
        )
        return data


class IikoDishesDbCache(database.BaseIikoDishes, CommonCacheDb):
    cache = get_cache_obj(key=config.CACHE_NAME)
    db = DbChoicer(db_name=config.DB_TYPE).choice_iiko_dishes_obj()

    async def get_data_by_dish_id(self, dish_id: int) -> Union[db_schemas.iiko.IikoDishSchem, None]:
        """Извлекаем данные блюда iiko по блюду из нашей системы к которой он относится
        Args:
            dish_id: идентификатор блюда (FK)
        """
        data = await self.search_in_cache_or_db_and_save(
            key=f"iiko_dish:dish:{dish_id}",
            db_func=self.db.get_data_by_dish_id,
            schema=db_schemas.iiko.IikoDishSchem,
            live_time=60,
            args=(dish_id,)
        )
        return data