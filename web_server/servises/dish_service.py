from typing import Any
import logging
import os

from ultralytics import YOLO
import cv2
import numpy as np

from storage.storage_core import StorageCommon
from schemas import logic_schemas

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