from typing import Any
import logging

from ultralytics import YOLO
import cv2
import numpy as np

from storage.storage_core import StorageCommon

logger = logging.getLogger(f"app.{__name__}")


class AiKassaService(StorageCommon):

    async def get_prediction_data(
            self,
            customer_id: int,
            menu_id: int,
            file_data: Any,
    ):
        """При помощи компьютерного зрения разбираем что изображено на фото
        и возвращаем объект обработанные данные обратно
        Args:
            customer_id: идентификатор заказчика
            menu_id: идентификатор меню
            file_data: фотография, на которой требуется распознать данные
        """

        logger.info(f"Пришел запрос на распознавание фотографии относящейся к customer_id: {customer_id}, menu_id: {menu_id}")
        menu_data = await self.menu_obj.get_data_by_id(node_id=menu_id)

        # создаем модель для распознавания
        model = YOLO(menu_data.ai_model_name)

        np_array = np.frombuffer(file_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        results = model(image)

        total_list = []

        for result in results:
            if result.boxes:
                for index, value in enumerate(result.boxes.xyxy):
                    # print("Here")
                    # print("value: ", value)
                    # print("integer_code: ", result.boxes.cls[index])
                    # print("code_name: ", result.names[int(result.boxes.cls[index])])
                    one_dish = await self.create_one_dish_obj(
                        menu_id=menu_id,
                        code_name=result.names[int(result.boxes.cls[index])],
                        x1=float(value[0]),
                        y1=float(value[1]),
                        x2=float(value[2]),
                        y2=float(value[3]),
                    )
                    if one_dish:
                        total_list.append(one_dish)
        return total_list


    async def create_one_dish_obj(
            self,
            menu_id: int,
            code_name: str,
            x1: float,
            y1: float,
            x2: float,
            y2: float
    ):
        """Данный метод формирует данные по одному блюду в необходимый словарь
        Args:
            menu_id: идентификатор меню, к которому относится блюдо
            code_name: кодовое имя блюда (для поиска его в БД)
            x1, y1, x2, y2 - координаты объекта
        """
        try:
            logger.info(f"Ищу блюдо в БД по code_name: {code_name}, menu_id: {menu_id}")

            dish_data = await self.dish_obj.get_data_by_menu_and_code_name(
                menu_id=menu_id, code_name=code_name
            )
            if dish_data:
               return {
                   "dish_data": dish_data.model_dump(),
                   "x1": x1,
                   "y1": y1,
                   "x2": x2,
                   "y2": y2
               }
        except Exception as _ex:
            logger.error(f"Ошибка при поиске блюда. menu_id: {menu_id}, code_name: {code_name}")