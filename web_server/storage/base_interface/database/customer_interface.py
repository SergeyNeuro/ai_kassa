from abc import ABC
from typing import Optional

from schemas import db_schemas


class BaseCustomer(ABC):
    """Интерфейс класс хранящий данные о заказчике"""
    async def get_data_by_email(self, email: str) -> Optional[db_schemas.customer.CustomersSchem]:
        """Извлечение данных заказчика по email
        """
        pass
