import requests
import logging
from typing import Optional

import requests

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
            response = requests.post(
                url=self.base_url,
                headers={"AggregatorAuthentication": self.token},
                json=payload
            )
            logger.info(f"Пришел ответ от r-keeper на запрос payload: {payload} -> {response.status_code}")
            return response.json()
        except Exception as _ex:
            logger.error(f"Ошибка при отправке запроса в r-keeper. payload: {payload} -> {_ex}")

    async def blank_method(self, menu_id: int):
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
        logger.info(f"Вызываю пустой метод проверки: {payload}")
        return True



    # def get_menu(self, r_keeper_):

    def create_order(self):
        data = {
            'taskType': 'CreateOrder',
            'params': {
                'sync': {
                    'objectId': 305320001,
                    'timeout': 120
                },
                'order': {
                    # 'originalOrderId': '777',
                    # 'customer': {
                    #     'name': 'customerName',
                    #     'phone': '111-222-333',
                    #     'email': 'email@test.ru'
                    # },
                    'payment': {
                        'type': 'online'
                    },
                    'expeditionType': 'pickup',
                    'pickup': {
                        # 'courier': {
                        #     'name': 'courierName',
                        #     'phone': '12-34-56'
                        # },
                        'expectedTime': '2025-02-15T11:00:00+03:00',
                        'taker': 'customer'
                    },
                    'products': [
                        {
                            'id': 1029341,
                            'name': 'Тест 1',
                            'price': '1',
                            'quantity': 1
                        }
                    ],
                    'comment': 'commentString',
                    'price': {
                        'total': 1
                    },
                    'personsQuantity': 1
                }
            }
        }

        data = {
            "taskType": "GetMenu",
            "params": {
                'sync': {
                    'objectId': 305320001,
                    'timeout': 120
                },
            }
        }

        headers = {
            "AggregatorAuthentication": "jN+y3tJvAd4=YrgXQ8/FD0CZ6ANaPBBe3JfQZ+vEUkHtpD+CUm5moketVby7nd+zlxWRuWbLPYr+7X0xHn/Lz/QpmFCtK4oyMs0xkBB7t9x3Z1MKUyDzI7rxXwpTwW5OGMfqp41SXUsKqSfER6v9X7seK6eGsSMCZ+arOZSiaVwzH7xbgBVGJMYnqATFVDpGK1WHpdANb3LzwwaMo5wh9nL5c0dFbqRJIfYRTP/lZfZx"
        }

        url = "https://ws.ucs.ru/wsserverlp/api/v2/aggregators/Create"

        response = requests.post(url=url, headers=headers, json=data)
        print(response.json())


if __name__ == '__main__':
    obj = RKeeper()
    print(obj.create_order())