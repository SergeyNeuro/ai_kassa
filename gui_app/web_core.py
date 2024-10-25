from copy import deepcopy
from typing import Union

import requests
from PIL import Image
import numpy as np
from io import BytesIO
import datetime as dt

# имитация
from imit import imit_data


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

    def send_image_to_predict(
            self,
            image: np.ndarray,
            menu_id: int = 2,
            url: str = "http://0.0.0.0:7770/"
    ) -> Union[list, None]:
        """Метод для отправки фотографии на удаленный сервер
        Args:
            image: изображение в формате numpy.ndarray
            menu_id: идентификатор меню, к которому относится отправляемое блюдо
            url: адрес куда нужно отправлять фотографию
        """
        try:
            # Преобразуем массив NumPy в объект PIL
            pil_image = Image.fromarray(image)

            # Сохраняем изображение в байтовый поток
            img_byte_arr = BytesIO()
            pil_image.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)  # Перемещаем указатель в начало потока

            print(f"Отправляю файл на по адресу: {url}")

            response = requests.post(
                url=f"{url}/api/predict",
                files={"file": img_byte_arr},
                params={"menu_id": menu_id, "timestamp": int(dt.datetime.now().timestamp())},
                headers={"AuthToken": "test"},
            )
            print(f"Пришел ответ от сервера: {response.json()}")
            if response.json().get("success"):
                message = "Фотография успешно сохранена на сервере"
                return response.json()["data"]
            else:
                message = "Не удалось сохранить фотографию на сервере"
        except Exception as _ex:
            print(f"Ошибка при отправке фотографии на сервер -> {_ex}")


