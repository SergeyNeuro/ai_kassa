from abc import ABC, abstractmethod
from typing import Union


from schemas import db_schemas


class BaseIikoCredentials(ABC):
    """Интерфейсный класс работы авторизации с r-keeper"""

    @abstractmethod
    async def get_data_by_menu_id(self, menu_id: int) -> Union[db_schemas.iiko.IikoCredentialsSchem, None]:
        """Извлекаем креденшиалс по внешнему ключу - идентификатору меню
        Args:
            menu_id: идентификатор меню (FK)
        """
        pass


class BaseIikoTerminals(ABC):
    """Интерфейсный класс работы авторизации с iiko"""

    @abstractmethod
    async def get_data_by_kassa_id(self, kassa_id: int) -> Union[db_schemas.iiko.IikoTerminalsSchem, None]:
        """Извлекаем данные терминала iiko по кассе к которой он относится
        Args:
            kassa_id: идентификатор кассы (FK)
        """
        pass


class BaseIikoDishes(ABC):
    """Интерфейсный класс работы блюд с iiko"""

    @abstractmethod
    async def get_data_by_dish_id(self, dish_id: int) -> Union[db_schemas.iiko.IikoDishSchem, None]:
        """Извлекаем данные блюда iiko по блюду из нашей системы к которой он относится
        Args:
            dish_id: идентификатор блюда (FK)
        """
        pass