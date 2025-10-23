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

    async def get_prediction_data(
            self,
            customer_id: int,
            menu_id: int,
            file_data: Any,
    ):
        """
        Распознаёт изображение YOLO-моделью, возвращает:
        - total_list: список распознанных блюд в прежнем формате (с координатами)
        - image_url: относительный URL до сохранённого изображения с нарисованными рамками
        """
        logger.info(f"Запрос на распознавание: customer_id={customer_id}, menu_id={menu_id}")

        # 1) Готовим модель
        menu_data = await self.menu_obj.get_data_by_id(node_id=menu_id)

        models_dir_path = os.path.join(STATIC_FILES_PATH, "models")
        os.makedirs(models_dir_path, exist_ok=True)

        model_path = os.path.join(models_dir_path, menu_data.ai_model_name)
        if not os.path.exists(model_path):
            logger.error(f"Файл модели не найден: {model_path}")
            raise FileNotFoundError(f"Модель не найдена: {model_path}")

        model = YOLO(model_path)

        # 2) Декодим изображение из байтов
        np_array = np.frombuffer(file_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Не удалось декодировать изображение")

        # 3) Инференс
        results = model(image)
        total_list = []
        output_image = image.copy()

        # 4) Разбираем боксы, собираем блюда и рисуем рамки
        for r in results:
            if not getattr(r, "boxes", None):
                continue

            # r.boxes.xyxy — тензор Nx4, r.boxes.cls — классы (индексы)
            xyxys = r.boxes.xyxy.tolist()
            clss = r.boxes.cls.tolist() if hasattr(r.boxes, "cls") else [0] * len(xyxys)

            for idx, box in enumerate(xyxys):
                x1, y1, x2, y2 = [int(v) for v in box]
                cls_id = int(clss[idx]) if idx < len(clss) else 0
                cls_name = r.names[cls_id] if hasattr(r, "names") else str(cls_id)

                # Собираем один item (как раньше)
                one_dish = await self.create_one_dish_obj(
                    menu_id=menu_id,
                    code_name=cls_name,
                    x1=x1, y1=y1, x2=x2, y2=y2
                )
                if one_dish:
                    total_list.append(one_dish)

                # Рисуем рамку
                cv2.rectangle(output_image, (x1, y1), (x2, y2), (0, 255, 0), 3)

                # Подпись класса (безопасно по Y)
                label_y = max(y1 - 10, 20)
                cv2.putText(
                    output_image,
                    cls_name,
                    (x1, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),
                    2
                )

                logger.info(f"Найден объект: {cls_name} [{x1},{y1},{x2},{y2}]")

        # 5) Сохраняем изображение с рамками
        pred_dir = os.path.join(STATIC_FILES_PATH, "predict")
        os.makedirs(pred_dir, exist_ok=True)

        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"predict_{timestamp}.jpg"
        pred_path = os.path.join(pred_dir, filename)

        ok = cv2.imwrite(pred_path, output_image)
        if not ok:
            raise RuntimeError("Не удалось сохранить изображение с предиктом")

        logger.info(f"Сохранено изображение с рамками: {pred_path}")

        # 6) Возвращаем итог
        return {
            "total_list": total_list,
            "image_url": f"/static/predict/{filename}",
        }


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