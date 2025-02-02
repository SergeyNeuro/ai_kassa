from abc import ABC, abstractmethod
from typing import Union


from schemas import db_schemas


class BaseRKeeperCredentials(ABC):
    """Интерфейсный класс работы авторизации с r-keeper"""
    @abstractmethod
    async def get_data_by_id(self, node_id: int) -> Union[db_schemas.r_keeper_credentials.RKeeperCredentialsSchem, None]:
        """Интерфейсный метод извлечения данных по первичному ключу
        Args:
            node_id: идентификатор записи (PK)
        """
        pass

    @abstractmethod
    async def get_data_by_menu_id(self, menu_id: int) -> Union[db_schemas.r_keeper_credentials.RKeeperCredentialsSchem, None]:
        """Извлекаем креденшиалс по внешнему ключу - идентификатору меню
        Args:
            menu_id: идентификатор меню (FK)
        """
        pass