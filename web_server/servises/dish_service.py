import logging
from typing import List

from storage.storage_core import StorageCommon
from schemas import logic_schemas
from servises.r_keeper import RKeeper

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
        logger.info(f"Пришел запрос на подтвержение покупки через кассу: {kassa_id}. menu_id: {menu_id}. data: {dishes_data}")
        # извлекаем данные меню
        menu_data = await self.menu_obj.get_data_by_id(node_id=menu_id)

        method_dict = {
            "r-keeper": self.confirm_r_keeper_order
        }
        return await method_dict[menu_data.system_name](menu_id, kassa_id, dishes_data)

    async def confirm_r_keeper_order(
            self,
            menu_id: int,
            kassa_id: int,
            dishes_data: logic_schemas.ai_kassa_predict.ConfirmSchem
    ):
        """Подтверждение заказа если работает конкретно с системой r-keeper
        Args:
            menu_id: идентификатор меню
            kassa_id: идентификатор кассового аппарата
            dishes_data: данный блюд по которым нужно подтвердить покупку
        """
        logger.info(f"Пришел запрос на подтвержение покупки r-keeper через кассу: {kassa_id}. menu_id: {menu_id}. data: {dishes_data}")
        obj = RKeeper()
        return await obj.blank_method(menu_id=menu_id)