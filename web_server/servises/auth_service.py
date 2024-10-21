"""auth/servises/auth_services"""

import logging
from typing import Union
import traceback as tr

from fastapi import Header

# импортируем объекты бизнес-логики
from storage.storage_core import StorageCommon
from schemas import db_schemas

logger = logging.getLogger(f"app.{__name__}")


async def get_token_by_headers(token: str = Header(alias="AuthToken", default=None)) -> Union[str, None]:
    """Данный метод извлекает токен из заголовка приходящего запроса
    Args:
        token: токен, который пришел в заголовке запроса
    """
    logger.info(f"Получен токен: {token}")
    return token


class AuthObj(StorageCommon):
    """Объект необходим для проверки аутентификации
    токена из приходящих запросов
    """

    async def check_authenticate(self, token: Union[str, None], api: str) -> Union[db_schemas.auth.AuthSchem, None]:
        """Данный метод проверяет есть ли данный токен в нашей системе
        и возвращает данные аутентфикации по данному токену
        Args:
            token: токен, который необходимо проверить
            api: ручка на который произошла ошибка
        """
        try:
            if token:
                # если токен не None
                logger.info(f"Проверяю токен: {token}")
                auth_data = await self.auth_obj.get_data_by_token(token=token)
                return auth_data if auth_data else None
        except Exception as _ex:
            logger.error(f"Ошибка аутентификации. Api: {api}. Token: {token}")
