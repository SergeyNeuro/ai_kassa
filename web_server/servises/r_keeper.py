import httpx
import logging
from typing import Optional, List, Dict, Union
import datetime as dt

from storage.storage_core import StorageCommon


logger = logging.getLogger(f"app.{__name__}")


class RKeeper(StorageCommon):
    base_url: str = "https://ws.ucs.ru/wsserverlp/api/v2/aggregators/Create"

    def __init__(self):
        self.object_id: Optional[int] = None
        self.token: Optional[str] = None

    async def pull_object(self, menu_id: int):
        """Данный метод наполняет объект необходимыми переменными
        чтобы можно было взаимодействовать с r-keeper
        Args:
            menu_id: идентификатор меню
        """
        data = await self.r_keeper_credentials.get_data_by_menu_id(menu_id=menu_id)
        if data:
            self.object_id = data.object_id
            self.token = data.token

    async def base_method(self, payload: dict):
        """Базовы метод отправки запроса в систему r-keeper
        Args:
            payload: тело запроса
        """
        try:
            response = httpx.post(
                url=self.base_url,
                headers={"AggregatorAuthentication": self.token},
                json=payload
            )
            logger.info(f"Пришел ответ от r-keeper на запрос payload: {payload} -> {response.status_code}")
            return response.json()
        except Exception as _ex:
            logger.error(f"Ошибка при отправке запроса в r-keeper. payload: {payload} -> {_ex}")

    async def get_menu(self, menu_id: int):
        if not self.object_id or self.token:
            await self.pull_object(menu_id=menu_id)
        payload = {
            "taskType": "GetMenu",
            "params": {
                'sync': {
                    'objectId': self.object_id,
                    'timeout': 120
                },
            }
        }
        return await self.base_method(payload=payload)

    async def create_order(self, menu_id: int, product_list: List[Dict[str, Union[str, int, float]]], total_price: float):
        if not self.object_id or self.token:
            await self.pull_object(menu_id=menu_id)
        payload = {
            'taskType': 'CreateOrder',
            'params': {
                'sync': {
                    'objectId': self.object_id,
                    'timeout': 120
                },
                'order': {
                    'payment': {
                        'type': 'online'
                    },
                    'products': product_list,
                    'comment': 'Smart Kassa',
                    'price': {
                        'total': total_price
                    },
                }
            }
        }

        return await self.base_method(payload=payload)

    async def confirm_order(self, menu_id: int, task_guid: str):
        """Подтверждение заказа
        Args:
            menu_id: меню к которому относится заказ
            task_guid: идентификатор заказа
        """
        logger.info(f"подтверждаю заказ: {task_guid} в меню: {menu_id}")
        if not self.object_id or self.token:
            await self.pull_object(menu_id=menu_id)
        payload = {
            "taskType": "CompleteOrder",
            "params": {
                "sync": {
                    "objectId": self.object_id,
                    "timeout": 120
                },
                "orderGuid": task_guid
            }
        }
        return await self.base_method(payload=payload)


if __name__ == '__main__':
    import asyncio
    async def main():
        obj = RKeeper()
        # пример создания заказа
        products_list = [
            {
                'id': 1029341,
                'name': 'Тест 1',
                'price': '1',
                'quantity': 1
            }
        ]
        total_price = 1
        res = await obj.create_order(menu_id=2, product_list=products_list, total_price=total_price)
        print(res)

    asyncio.run(main())