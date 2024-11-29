from copy import deepcopy
from typing import Union
import logging

import requests
from PIL import Image
import numpy as np
from io import BytesIO
import datetime as dt
import cv2

# глобальные настройки
from config import WEB_SERVER_URL, TOKEN, MENU_ID

logger = logging.getLogger(f"app.{__name__}")


class TestWebCore:
    """Класс для взаимодействия с веб сервером"""

    def send_image_to_predict(self, image: np.ndarray):
        """Отправка изображения с блюдами для распознавания нейросетью на удаленный сервер
        Args:
            image: изображение в формате массива numpy
        """
        return deepcopy(imit_data)


class WebCore:
    """Класс для взаимодействия с веб сервером"""

    @staticmethod
    def send_image_to_predict(
            image: np.ndarray,
            menu_id: int = MENU_ID,
            url: str = WEB_SERVER_URL
    ) -> Union[list, None]:
        """Метод для отправки фотографии на удаленный сервер
        Args:
            image: изображение в формате numpy.ndarray
            menu_id: идентификатор меню, к которому относится отправляемое блюдо
            url: адрес куда нужно отправлять фотографию
        """
        try:
            # Преобразуем массив NumPy в объект PIL
            rgb_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            pil_image = Image.fromarray(rgb_frame)

            # Сохраняем изображение в байтовый поток
            img_byte_arr = BytesIO()
            pil_image.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)  # Перемещаем указатель в начало потока

            logger.info(f"Отправляю файл на по адресу: {url}/api/predict")

            response = requests.post(
                url=f"{url}/api/predict/",
                files={"file": img_byte_arr},
                params={"menu_id": menu_id, "timestamp": int(dt.datetime.now().timestamp())},
                headers={"AuthToken": TOKEN},
            )
            logger.info(f"Пришел ответ от сервера: {response.json()}")
            if response.json().get("success"):
                message = "Фотография успешно сохранена на сервере"
                return response.json()["data"]
            else:
                message = "Не удалось сохранить фотографию на сервере"
        except Exception as _ex:
            logger.error(f"Ошибка при отправке фотографии на сервер -> {_ex}")

    @staticmethod
    def send_dataset_photo(
            image: np.ndarray,
            menu_id: int = int(MENU_ID),
            url: str = WEB_SERVER_URL
    ) -> bool:
        """Метод для отправки фотографии на удаленный сервер
        Args:
            photo_path: путь до фотографии
            menu_id: идентификатор меню, к которому относится отправляемое блюдо
            url: адрес куда нужно отправлять фотографию
        """
        try:
            rgb_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            pil_image = Image.fromarray(rgb_frame)

            # Сохраняем изображение в байтовый поток
            img_byte_arr = BytesIO()
            pil_image.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)  # Перемещаем указатель в начало потока

            logger.info(f"Отправляю файл на по адресу: {url}/api/dataset/upload/")

            response = requests.post(
                url=f"{url}/api/dataset/upload",
                files={"file": img_byte_arr},
                params={"menu_id": menu_id},
                headers={
                    "AuthToken": TOKEN,
                }
            )
            logger.info(f"Пришел ответ от сервера: {response.json()}")
            if response.json()["success"]:
                return True
            else:
                return False
        except Exception as _ex:
            logger.info(f"Ошибка при отправке фотографии на сервер -> {_ex}")
            return True

