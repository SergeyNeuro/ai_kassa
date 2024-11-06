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


if __name__ == '__main__':
    url = "https://app.neurotaw.beget.tech/api/predict/?menu_id=2&timestamp=1730721272"

    import requests
    response = requests.post(url=url)
    print(response.json())
