from typing import Any
import logging
import os
import datetime as dt

from ultralytics import YOLO
import cv2
import numpy as np

from storage.storage_core import StorageCommon
from config import STATIC_FILES_PATH
from schemas import logic_schemas, db_schemas

logger = logging.getLogger(f"app.{__name__}")


class AiKassaService(StorageCommon):
    async def get_prediction_data_for_test(
            self,
            menu_id: int,
            file_data: Any,
            token: str,
    ):
        """
        1)Распознаем какие блюда находятся на фотографии
        2)Соотносим с БД, что выставить верную цену и верное название товаров
        3)Рисуем боксы на изображении и сохраняем фотографию для демонстрации на web странице
        """

        logger.info(
            f"Пришел запрос на ТЕСТОВОЕ распознавание фотографии относящейся menu_id: {menu_id}")
        menu_data = await self.menu_obj.get_data_by_id(node_id=menu_id)

        models_dir_path = f"{STATIC_FILES_PATH}/models"

        os.makedirs(models_dir_path, exist_ok=True)

        # создаем модель для распознавания
        model = YOLO(f"{models_dir_path}/{menu_data.ai_model_name}")

        np_array = np.frombuffer(file_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        results = model(image)

        total_list = []

        for result in results:
            if result.boxes:
                for index, value in enumerate(result.boxes.xyxy):
                    one_dish = await self.create_one_dish_obj(
                        menu_id=menu_id,
                        code_name=result.names[int(result.boxes.cls[index])],
                        x1=int(value[0]),
                        y1=int(value[1]),
                        x2=int(value[2]),
                        y2=int(value[3]),
                    )
                    if one_dish:
                        total_list.append(one_dish)

        # сортируем по категориям
        total_list = sorted(total_list, key=lambda x: x["dish_data"]["type"])

        # рисуем на картинке боксы и сохраняем
        file_path = self.write_boxes_in_image(dishes_list=total_list, image=image)

        # сохраняем в КЭШ данные
        obj = logic_schemas.ai_kassa_predict.TestConfirmSchem.model_validate({"data": total_list})
        self.cache.set_data_in_cache(
            key=token,
            value=obj,
            live_time=30
        )


        return {"total_list": total_list, "image_url": file_path}

    @staticmethod
    def write_boxes_in_image(
            dishes_list: list,
            image: np.ndarray
    ) -> str:
        """Отрисовываем боксы на фотографии. Сохраняем измененную фотографии
        и возвращаем путь до нее
        """
        colors = {
            0: (0, 100, 0),
            1: (139, 0, 0),
            2: (0, 0, 139),
            3: (255, 255, 0),
            4: (255, 165, 0),
            5: (128, 0, 128),
            6: (127, 255, 0),
            7: (255, 192, 203),
            8: (135, 206, 235),
            9: (230, 230, 250),
            10: (0, 128, 0),
            11: (255, 0, 0),
            12: (0, 0, 255),
            13: (160, 32, 240),
            14: (144, 238, 144),
            15: (255, 127, 80),
            16: (173, 216, 230),
            17: (221, 160, 221),
            18: (0, 160, 0),
            19: (255, 99, 71),
            20: (70, 130, 180),
            21: (186, 85, 211)
        }

        for index, dish in enumerate(dishes_list):
            color = colors.get(index)

            cv2.rectangle(image, (dish["x1"], dish["y1"]), (dish["x2"], dish["y2"]), color, 3)

            # Подпись класса (безопасно по Y)
            label_y = max(dish["y1"] - 10, 20)
            cv2.putText(
                image,
                str(dish["dish_data"]["id"]),
                ((dish["x2"] - dish["x1"]) // 2 + dish["x1"] - 10, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                color,
                2
            )

        # 5) Сохраняем изображение с рамками
        pred_dir = os.path.join(STATIC_FILES_PATH, "predict")
        os.makedirs(pred_dir, exist_ok=True)

        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"predict_{timestamp}.jpg"
        pred_path = os.path.join(pred_dir, filename)

        ok = cv2.imwrite(pred_path, image)
        if not ok:
            raise RuntimeError("Не удалось сохранить изображение с предиктом")

        logger.info(f"Сохранено изображение с рамками: {pred_path}")
        return f"/predict/photo/{filename}"

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

        logger.info(
            f"Пришел запрос на распознавание фотографии относящейся к customer_id: {customer_id}, menu_id: {menu_id}")
        menu_data = await self.menu_obj.get_data_by_id(node_id=menu_id)

        models_dir_path = f"{STATIC_FILES_PATH}/models"

        os.makedirs(models_dir_path, exist_ok=True)

        # создаем модель для распознавания
        model = YOLO(f"{models_dir_path}/{menu_data.ai_model_name}")

        np_array = np.frombuffer(file_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        results = model(image)

        total_list = []

        for result in results:
            if result.boxes:
                for index, value in enumerate(result.boxes.xyxy):
                    one_dish = await self.create_one_dish_obj(
                        menu_id=menu_id,
                        code_name=result.names[int(result.boxes.cls[index])],
                        x1=int(value[0]),
                        y1=int(value[1]),
                        x2=int(value[2]),
                        y2=int(value[3]),
                    )
                    if one_dish:
                        total_list.append(one_dish)

        # сортируем по категориям
        total_list = sorted(total_list, key=lambda x: x["dish_data"]["type"])

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
                # проверяем является ли данная позиция сомневающейся
                if dish_data.changing_dish_id:
                    changing_dishes = await self.choice_changing_dish(dish_data=dish_data)
                    dish_data = changing_dishes.model_dump()["dish_list"]
                else:
                    dish_data = dish_data.model_dump()

                return {
                   "dish_data": dish_data,
                   "x1": x1,
                   "y1": y1,
                   "x2": x2,
                   "y2": y2
               }
        except Exception as _ex:
            logger.error(f"Ошибка при поиске блюда. menu_id: {menu_id}, code_name: {code_name}")

    async def choice_changing_dish(self, dish_data: db_schemas.dish.DishSchem):
        """Находим все похожие блюда чтобы клиент мог их них выбрать
        Args:
            dish_data: данные одного блюда
        """
        logger.info(f"Блюдо: {dish_data} сомневающееся, извлекаем список позиций")
        # используем паттерн стратегия
        changing_data = await self.changing_dish_obj.get_data_by_id(node_id=dish_data.changing_dish_id)

        method_dict = {
            "all_dish": self.get_all_dish_by_changing,
            "week_day_dish": self.get_week_day_dish
        }
        return await method_dict[changing_data.strategy](dish_data.changing_dish_id)

    async def get_all_dish_by_changing(self, changing_id: int) -> db_schemas.dish.DishListSchem:
        """Извлечение всех блюд по внешнему ключу - ссылке на
        таблицу с сомневающимися продуктами
        Args:
            changing_id: (FK) ссылка на сомневающиеся продукты
        """
        return await self.dish_obj.get_data_by_changing_id(changing_id=changing_id)

    async def get_week_day_dish(self, changing_id: int) -> db_schemas.dish.DishListSchem:
        """Извлечение всех блюд по внешнему ключу - ссылке на
        таблицу с сомневающимися продуктами и сегодняшнему дню недели
        Args:
            changing_id: (FK) ссылка на сомневающиеся продукты
        """
        return await self.week_day_dish.get_dish_list_by_week_day_and_changing_id(
            changing_id=changing_id, week_day=dt.datetime.today().weekday()
        )

if __name__ == '__main__':
    import asyncio
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")

    obj = AiKassaService()
    async def main():
        data = await obj.get_week_day_dish(changing_id=3)
        print(data)

    asyncio.run(main())