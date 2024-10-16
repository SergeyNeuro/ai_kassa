"""storage/db_cache/common
Модуль содержащий родительский класс содержащий методы
характерные для всей логики взаимодействия по правилам
cache_db
"""

import logging
from typing import Callable, Type, Union

from pydantic import BaseModel

from storage.database.cache.cache_choicer import get_cache_obj
from storage.base_interface.cache.cache_interface import BaseCache

from config import CACHE_NAME


logger = logging.getLogger(f"app.{__name__}")


class CommonCacheDb:
    """В данном классе инкапсулированы методы взаимодействия
    с КЭШем общие для всех взаимодействий с ним
    """
    cache: BaseCache = get_cache_obj(CACHE_NAME)

    async def search_in_cache_or_db_and_save(
            self,
            key: str,
            db_func: Callable,
            schema: Type[BaseModel],
            live_time: int,
            args: tuple
    ) -> Union[BaseModel, None]:
        """Данный метод ищет Pydantic объект в Redis. Если он его не находит,
        то ищет в БД. Если нашел в БД то сохраняет метод
        Args:
            key: ключ по которому данные извлекаются или сохраняются в КЭШ
            schema: Pydantic схема для валидации данных
            db_func: функция извлечения данных из БД
            live_time: время, которое данные должны храниться в КЭШе
            args: кортеж аргументов, которые будут переданы в метод обращения к БД
        """
        data: Union[schema, None] = self.cache.get_data_from_cache(key=key, data_class=schema)
        if data:    # если обнаружили в КЭше
            logger.info(f"Извлек данные из КЭШа: {data}")
            return data
        else:   # если в КЭШе не обнаружено - то ищем в БД
            # вызываем корутину обращения к БД
            data: Union[schema, None] = await db_func(*args)
            if data:    # если данные обнаружены в БД
                logger.info(f"Извлек данные из БД: {data}")
                self.cache.set_data_in_cache(key=key, value=data, live_time=live_time)
                return data

