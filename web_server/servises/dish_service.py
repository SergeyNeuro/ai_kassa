import asyncio
import logging
from typing import List
import re

from sqlalchemy.util import await_only

from storage.storage_core import StorageCommon
from schemas import logic_schemas
from servises.r_keeper import RKeeper
from servises.iiko import IikoAPI

logger = logging.getLogger(f"app.{__name__}")


class DishService(StorageCommon):
    """Объект отвечающий за логику обработки блюда из меню"""

    async def add_new_dish(self, dish_data: logic_schemas.add_dish.DishSchem) -> bool:
        """Метод добавления нового блюде с предварительной проверкой есть ли такое в БД или нет"""
        logger.info(f"Добавляю новое блюдо: {dish_data}")
        # проверяем есть ли такое блюдо в БД
        dish_in_db = await self.dish_obj.get_data_by_menu_and_code_name(
            menu_id=dish_data.menu_id, code_name=dish_data.code_name
        )
        if dish_in_db:
            return False
        else:
            dish_in_db = await self.dish_obj.add_new_dish(
                **dish_data.model_dump()
            )
            if dish_in_db:
                return True
            else:
                return False

    async def confirm_pay(
            self,
            menu_id: int,
            kassa_id: int,
            dishes_data: List[logic_schemas.ai_kassa_predict.ConfirmSchem]
    ):
        """Метод для подтверждения покупки через кассу.
        Нужен чтобы занести результаты в системы (например в r-keeper
        Args:
            menu_id: идентификатор меню
            kassa_id: идентификатор кассового аппарата
            dishes_data: Данные по покупке
        """
        logger.info(f"Пришел запрос на подтверждение покупки через кассу: {kassa_id}. menu_id: {menu_id}. data: {dishes_data}")
        # извлекаем данные меню
        menu_data = await self.menu_obj.get_data_by_id(node_id=menu_id)

        method_dict = {
            "r-keeper": self.confirm_r_keeper_order,
            "iiko": self.confirm_iiko_order
        }
        return await method_dict[menu_data.system_name](menu_id, kassa_id, dishes_data)

    async def confirm_r_keeper_order(
            self,
            menu_id: int,
            kassa_id: int,
            dishes_data: List[logic_schemas.ai_kassa_predict.ConfirmSchem]
    ) -> bool:
        """Подтверждение заказа если работает конкретно с системой r-keeper
        Args:
            menu_id: идентификатор меню
            kassa_id: идентификатор кассового аппарата
            dishes_data: данный блюд по которым нужно подтвердить покупку
        """
        logger.info(f"Пришел запрос на подтвержение покупки r-keeper через кассу: {kassa_id}. menu_id: {menu_id}. data: {dishes_data}")
        obj = RKeeper()

        # получаем список продуктов + цену необходимые для системы r-keeper
        products_list, total_price = await self.create_r_keeper_product_list(dishes_data=dishes_data)
        # отправляем запрос на создания заказа
        order_data = await obj.create_order(menu_id=menu_id, product_list=products_list, total_price=total_price)
        if "taskResponse" in order_data:
            order_guid = order_data["taskResponse"]["order"]["orderGuid"]

            confirm = await obj.confirm_order(menu_id=menu_id, task_guid=order_guid)
            if "error" in confirm:
                return False
            return True
        return False

    async def confirm_iiko_order(
            self,
            menu_id: int,
            kassa_id: int,
            dishes_data: List[logic_schemas.ai_kassa_predict.ConfirmSchem]
    ) -> bool:
        """Подтверждение заказа если работает конкретно с системой iiko
        Args:
            menu_id: идентификатор меню
            kassa_id: идентификатор кассового аппарата
            dishes_data: данный блюд по которым нужно подтвердить покупку
        """
        logger.info(f"Пришел запрос на подтвержение покупки r-iiko через кассу: {kassa_id}. menu_id: {menu_id}. data: {dishes_data}")

        # получаем данные терминала через кассу
        iiko_terminal_data = await self.iiko_terminals_obj.get_data_by_kassa_id(kassa_id=kassa_id)
        # получаем данные организации
        creds_data = await self.iiko_credentials_obj.get_data_by_menu_id(menu_id=menu_id)
        # создаем список items из системы iiko + цены и кол-во
        items_list = list()
        for dish in dishes_data:
            item_data = await self.get_one_item_iiko_data(dish_data=dish)
            if item_data:
                items_list.append(item_data)

        create = await self.create_iiko_order_try_count(
            menu_id=menu_id,
            organization_id=creds_data.organization_id,
            terminal_id=iiko_terminal_data.terminal_id,
            items=items_list
        )

        logger.info(f"Результат создания заказа: {create}")
        return True

    async def create_iiko_order_try_count(
            self,
            menu_id: int,
            organization_id: str,
            terminal_id: str,
            items: List[logic_schemas.iiko.CreateIikoOrderSchem],
            try_count: int = 3,
            attempt: int = 1
    ) -> bool:
        """Создаем заказ в IIKO за несколько попыток и проверяем успешно ли он был создан"""
        logger.info(f"Пробрасываю заказ в IIKO. menu_id: {menu_id}, organization_id: {organization_id}, items: {items}, items: {items}")

        obj = IikoAPI(menu_id=menu_id)
        # создаем заказ
        create = await obj.create_order(
            organization_id=organization_id,
            terminal_group_id=terminal_id,
            items=items
        )
        if create:
            operation_id = create["correlationId"]
            return await self.check_creation_order_result(
                menu_id=menu_id,
                organization_id=organization_id,
                operation_id=operation_id
            )
        else:
            if attempt <= try_count:
                await asyncio.sleep(3)
                return await self.create_iiko_order_try_count(
                    menu_id=menu_id,
                    organization_id=organization_id,
                    terminal_id=terminal_id,
                    items=items,
                    attempt=attempt + 1
                )
            else:
                return False

    async def check_creation_order_result(
            self,
            menu_id: int,
            organization_id: str,
            operation_id: str,
            try_count: int = 3,
            attempt: int = 1
    ) -> bool:
        """Проверяем успешность создания заказа в iiko"""
        obj = IikoAPI(menu_id=menu_id)
        operation = await obj.get_command_status(
            correlation_id=operation_id, organization_id=organization_id
        )
        if operation:
            state = operation.get("state")
            if state == "Success":
                logger.info(f"Заказ успешно подтвержден")
                return True
            else:
                if attempt <= try_count:
                    await asyncio.sleep(3)
                    return await self.check_creation_order_result(
                        menu_id, organization_id, operation_id, try_count, attempt + 1
                    )
                else:
                    return False

        else:
            if attempt <= try_count:
                await asyncio.sleep(3)
                return await self.check_creation_order_result(
                    menu_id, organization_id, operation_id, try_count, attempt + 1
                )
            else:
                return False



    async def get_one_item_iiko_data(self, dish_data: logic_schemas.ai_kassa_predict.ConfirmSchem):
        """Из ID блюда и его названия получаем данные IIKO"""
        logger.info(f"Получаю данные по IIKO: {dish_data}")
        # ищем в БД по ID блюда
        iiko_item_data = await self.iiko_dishes_obj.get_data_by_dish_id(dish_id=dish_data.dish_data.id)
        return logic_schemas.iiko.CreateIikoOrderSchem(
            item_id=iiko_item_data.iiko_id,
            price=float(dish_data.dish_data.price),
            amount=float(dish_data.dish_data.count)
        )

    async def create_r_keeper_product_list(
            self,
            dishes_data: List[logic_schemas.ai_kassa_predict.ConfirmSchem]
    ) -> tuple[list, float]:
        """Создаем список словарей, который будет отправлен в r-keeper чтобы подтвердить заказ
        Args:
            menu_id: идентификатор меню к которому относятся блюда
            dishes_data: блюда которые были куплены
        return: возвращает список блюд + цену за все блюда
        """
        logger.info(f"Формирую список продукто в для r-keeper products: {dishes_data}")
        total_price = 0
        total_list = list()
        for dish in dishes_data:
            # извлекаем данные по эквивалетному блюду из r-keeper
            r_keeper_data = await self.r_keeper_dish.get_data_by_dish_id(dish_id=dish.dish_data.id)
            total_list.append({
                'id': r_keeper_data.r_keeper_id,
                'name': r_keeper_data.name,
                'price': round(float(dish.dish_data.price), 2),
                'quantity': dish.dish_data.count
            })
            total_price += dish.dish_data.price
        return total_list, round(float(total_price), 2)


    async def get_dish_by_barcode(self, menu_id: int, barcode: str):
        """Извлекаем данные блюда по штрихкоду"""
        digits = re.findall(r'\d', barcode)

        # Объединяем найденные цифры в одну строку
        barcode = ''.join(digits)

        logger.info(f"Извлекаем данные блюда по штрихкоду: {barcode} из меню: {menu_id}")
        return await self.dish_obj.get_data_by_menu_and_barcode(menu_id=menu_id, barcode=barcode)
