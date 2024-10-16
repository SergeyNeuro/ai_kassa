from abc import ABC, abstractmethod
from typing import Union


from schemas import db_schemas


class BaseAuth(ABC):
    """Интерфейсный класс работы с данными аутентификации"""
    @abstractmethod
    async def get_data_by_token(self, token: str) -> Union[db_schemas.auth.AuthSchem, None]:
        """Интерфейсный метод извлечения данных по токену
        Args:
            token: токен доступа, по которому осуществляется проверка
        """
        pass