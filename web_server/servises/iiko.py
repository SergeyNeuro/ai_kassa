import typing
import json
import httpx
import logging
import asyncio

from storage.storage_core import StorageCommon
from schemas import logic_schemas

logger = logging.getLogger(f"app.{__name__}")


class IikoAPI(StorageCommon):
    base_url_v1 = "https://api-ru.iiko.services/api/1/"
    base_url_v2 = "https://api-ru.iiko.services/api/2/"

    def __init__(self, menu_id: int):
        self.menu_id = menu_id
        self.token = None
        self.api_key = None

    async def base_request(
            self,
            api_url: str,
            method: str = "POST",
            version: int = 1,
            params: typing.Optional[dict] = None,
            body: typing.Optional[dict] = None
    ):
        """Базовый запрос для отправки в сервис AIKO"""
        if not self.token:
            await self.authorize()

        base_url = self.base_url_v1 if version == 1 else self.base_url_v2
        logger.info(f"Отправляю запрос на {base_url + api_url}")
        response = httpx.request(
            method=method,
            url=base_url + api_url,
            params=params,
            json=body,
            headers={"Authorization": f"Bearer {self.token}"}
        )

        logger.info(f"Результат вызова: {response.url} -> {response.json()}")
        return response.json()

    async def authorize(self):
        # проверяем не занесен ли токен в КЭШ
        token = self.cache.get_single_data_from_cache(key=f"iiko_token:menu:{self.menu_id}")
        if not token:
            if not self.api_key:
                key_data = await self.iiko_credentials_obj.get_data_by_menu_id(menu_id=self.menu_id)
                if not key_data:
                    logger.error(f"Отсутствует связка menu: {self.menu_id} и IIKO")
                    return False
                self.api_key = key_data.aki_key

            response = httpx.post(
                url=self.base_url_v1 + "access_token", json={"apiLogin": self.api_key}
            ).json()

            logger.info(f"Результат авторизации: {response}")

            # заносим значение переменной в аттрибут класса
            token = response["token"]
            # заносим значение токена в КЭШ на 1 час
            self.cache.set_single_data_in_cache(
                key=f"iiko_token:menu:{self.menu_id}", value=token, live_time=60 * 60
            )
        self.token = token

    async def get_organizations(self):
        return await self.base_request(
            api_url="organizations",
            body={
                "returnAdditionalInfo": False,
                "includeDisabled": False,
            }
        )

    async def get_terminals_groups(self, organization_id: str):
        """Запрашиваем список терминалов (касс)"""
        return await self.base_request(
            api_url="terminal_groups",
            body={"organizationIds": [organization_id], "includeDisabled": False}
        )

    async def get_terminals(self, organization_id: str, group_id: str):
        """Запрашиваем список терминалов (касс)"""
        return await self.base_request(
            api_url="terminal_groups/is_alive",
            body={"organizationIds": [organization_id], "terminalGroupIds": [group_id]}
        )

    async def get_menu(self, organization_id: str, menu_id: typing.Optional[str] = None):
        """Запрашиваем меню организации"""
        if menu_id:
            # извлекаем данные по одному конкретному меню
            return await self.base_request(
                api_url="menu/by_id",
                body={
                    "organizationIds": [organization_id],
                    "externalMenuId": menu_id,
                    "priceCategoryId": "00000000-0000-0000-0000-000000000000"
                },
                version=2
            )
        # извлекаем список всех возможных меню относящихся к организации
        return await self.base_request(
            api_url="menu",
            body={"organizationId": organization_id},
            version=2
        )

    async def create_order(
            self,
            organization_id: str,
            terminal_group_id: str,
            items: typing.List[logic_schemas.iiko.CreateIikoOrderSchem]
    ):
        """Создаем заказ"""

        return await self.base_request(
            api_url="order/create",
            body={
                "organizationId": organization_id,
                "terminalGroupId": terminal_group_id,
                "order": {
                    "items": [
                        {
                            "productId": item.item_id,
                            "price": item.price,
                            "type": "Product",
                            "amount": item.amount
                        } for item in items
                    ]
                }
            }
        )

    async def get_command_status(self, correlation_id: str, organization_id: str):
        """Узнаем статус того или иного действия"""
        return await self.base_request(
            api_url="commands/status",
            body={
                "organizationId": organization_id,
                "correlationId": correlation_id
            }
        )

    async def get_menu_data(self, organization_id: str, menu_id: str, save: bool = False):
        """Формируем JSON из меню выгруженного из IIKO"""
        # выгружаем меню
        menu = await self.get_menu(
            organization_id=organization_id, menu_id=menu_id
        )

        # проходимся в цикле и формируем словарь
        data = self.process_menu_dict(data=menu["itemCategories"])

        # сохраняем словарь как JSON файл
        if save:
            self._save_json(data=data)

        return data

    def process_menu_dict(self, data: list):
        """Формируем словарь с меню"""
        res = dict()
        for one_category in data:
            res[one_category["name"]] = self.process_category(data=one_category)

        return res

    def process_category(self, data: dict):
        """Обрабатываем данные одной категории"""
        res = list()
        for item in data["items"]:
            res.append(self.process_item(item))
        return res

    @staticmethod
    def process_item(data: dict):
        """Обрабатываем одно блюдо"""
        logger.info(f'{data["itemSizes"][0]["portionWeightGrams"]}')
        return {
            "name": data["name"],
            "price": data["itemSizes"][0]["prices"][0]["price"],
            "item_id": data["itemId"],
            "portion_gramm": data["itemSizes"][0]["portionWeightGrams"]
        }

    @staticmethod
    def _save_json(data: dict):
        """Сохраняем данные в JSON формате"""
        with open("data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
    async def main():
        obj = IikoAPI(menu_id=2)
        # res = await obj.get_menu_data(organization_id="c5dabafd-750c-4e36-ba91-5f0373e57361", menu_id="61447")
        res = await obj.get_command_status(organization_id="c5dabafd-750c-4e36-ba91-5f0373e57361",
                                      correlation_id="2893c940-e5f4-4487-8ff7-4ae4165a1534")
        print(res)
    asyncio.run(main())

    # data = obj.get_organizations()
    # data = obj.get_menu(organization_id=obj.organization_id)
    # data = obj.get_menu(organization_id=obj.organization_id, menu_id="61447")
    # data = obj.get_menu_data(organization_id=obj.organization_id, menu_id="56239", save=True)
    # data = obj.get_terminals_groups(organization_id=obj.organization_id)
    # data = obj.create_order(organization_id=obj.organization_id, terminal_group_id=obj.terminal_group_id)
    # data = obj.get_command_status(organization_id="c5dabafd-750c-4e36-ba91-5f0373e57361", correlation_id="7503a2c1-25ad-437b-8b80-501c9cc0b986")

    # print(data)