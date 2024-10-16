"""storage/database/cache_db/auth"""

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


class AuthDbCache(database.BaseAuth, CommonCacheDb):
    cache = get_cache_obj(key=config.CACHE_NAME)
    db = DbChoicer(db_name=config.DB_TYPE).choice_auth_obj()

    async def get_data_by_token(self, token: str) -> Union[db_schemas.auth.AuthSchem, None]:
        """Метод для извлечения данных по токену.
        Сначала ищем в КЭШе, потом в БД
        Args:
            token: токен доступа, по которому осуществляется проверка
        """
        logger.debug(f"Извлекаю данные по токену: {token}")
        data = await self.search_in_cache_or_db_and_save(
            key=token,
            db_func=self.db.get_data_by_token,
            schema=db_schemas.auth.AuthSchem,
            live_time=60,
            args=(token,)
        )
        logger.debug(f"Извлек данные по токену -> {data}")
        return data
