import requests
from typing import List, Union, Optional
import logging
import time

from pydantic import BaseModel
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)



class DishSchem(BaseModel):
    name: Optional[str]
    menu_id: Optional[int]
    code_name: Optional[str]
    type: Optional[int]
    count_type: Optional[int]
    count: Optional[int]
    price: Optional[int]
    changing_dish_id: Optional[int]


class StartDialogSender:
    def __init__(self, file_path: str, token: str, url: str = 'http://127.0.0.1:8000/api/dataset/dish'):
        """Инициализация класса
        Args:
            url: адрес на который необходимо отправить запрос для добавления данных
            token: токен безопасности для доступа к API ядра
            file_path: путь до Excel файла, из которого необходимо прочитать стартовые диалоги
        """
        self.url = url
        self.token = token
        self.file_path = file_path

    def post_request(self, data: List[DishSchem]) -> None:
        """Данный метод отправляет запрос в ЯДРО для добавления пачки стартовых диалогов
        Args:
            data: список данных которые необходимо отправить
        """
        for body in data:
            headers = {"Content-Type": "application/json", "auth_token": self.token}
            response = requests.post(url=self.url, json=body.model_dump(), headers=headers)
            logger.info(f"Пришел ответ от ЯДРА: {response.json()}")
            time.sleep(0.1)
            print(response.json())

    def read_file(self) -> pd.DataFrame:
        """Данный метод считывает excel файл и преобразует его в Pandas объект"""
        logger.info(f"Читаю данные из Excel файла: {self.file_path}")
        df = pd.read_excel(self.file_path, index_col=False)
        df = df.replace({np.nan: None})
        return df

    @staticmethod
    def validate_data(df):
        # Преобразуйте DataFrame в список объектов Pydantic
        return [DishSchem(**row) for index, row in df.iterrows()]

    def send_start_dialogs_in_core(self):
        """Данный метод выполняет всю логику отправки стартовых диалогов в ЯДРО"""
        data = self.validate_data(df=self.read_file())  # читаем данные из файла и валидируем их
        self.post_request(data=data)


if __name__ == '__main__':
    obj = StartDialogSender(
        token="test",
        file_path="all_dish.xlsx"
    )
    obj.send_start_dialogs_in_core()
