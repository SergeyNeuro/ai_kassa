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

    async def for_test_auth(
            self,
            login: str,
            password: str,
            menu_id: int,
            kassa_id: int
    ) -> bool:
        """Проводим аутентификацию пользователя
        1)Извлекаем данные по логику
        2)Проверяем совпадает ли пароль
        3)Проверяем закреплено ли данное меню за пользователем
        4)Проверяем закреплена ли данная касса за меню
        """
        customer_data = await self.customers_obj.get_data_by_email(email=login)
        if not customer_data:
            return False
        if customer_data.password != password:
            return False
        menu_data = await self.menu_obj.get_data_by_id(node_id=menu_id)
        if not menu_data:
            return False
        if menu_data.customer_id != customer_data.id:
            return False
        kassa_data = await self.kassa_obj.get_data_by_id(node_id=kassa_id)
        if not kassa_data:
            return False
        food_point_data = await self.food_point.get_data_by_id(node_id=kassa_data.food_point_id)
        if not food_point_data:
            return False
        if food_point_data.customer_id != customer_data.id:
            return False

        # прошли все проверки. Аутентификация успешна
        return True

