from dotenv import load_dotenv
import os
from typing import Type, Union
import logging

from pydantic import BaseModel, ValidationError
import redis


# Выгрузка секретных данных из .env. Данный файл должен лежать в данной директории.
load_dotenv()
logger = logging.getLogger(f"app.{__name__}")


class Redis:
    """Объект для взаимодействия с redis"""

    def __init__(self, port=os.getenv("REDIS_PORT"), password=os.getenv("REDIS_PASSWORD"), host=os.getenv("REDIS_HOST")):
        self.redis = redis.from_url(f"redis://:{password}@{host}:{port}")

    def get_data_from_cache(self, key: str, data_class: Type[BaseModel]) -> Union[BaseModel, None]:
        """Данный метод ищет данные в КЭШе по ключу и преобразует в pydantic"""
        try:
            logger.info(f"Извлекаю данные из КЭШа по ключу: {key}")
            json_data = self.redis.get(key)
            if json_data:
                return data_class.model_validate_json(json_data)
            logger.debug(f"Данные в КЭШе по ключу: {key} не найдены")
        except ValidationError:
            error_text = f"Ошибка валидации данных по ключу: {key}. Data class: {data_class}"
            logger.error(error_text)
        except Exception as _ex:
            logger.critical(f"Ошибка извлечения pydantic по ключу: {key} из redis => {_ex}")

    def set_data_in_cache(self, key: str, value: BaseModel, live_time: int) -> bool:
        """Данный метод заносит в КЭШ Pydantic объект
        Args:
            key: ключ по которому заносится объект
            value: значение которое будет спрятано под ключем
            live_time: время в секундах сколько хранится значение в КЭШе
        """
        try:
            logger.info(f"Сохраняю pydantic объект в КЭШ по ключу: {key} на {live_time} секунд")
            self.redis.set(key, value.model_dump_json(), ex=live_time)
            return True
        except Exception as _ex:
            logger.critical(f"Ошибка занесения pydantic объекта по ключу {key} => {_ex}")
            return False

    def delete_data_from_cache(self, key: str):
        """Данный метод удаляет данные из КЭШа по ключу
        Args:
            key: ключ, по которому необходимо удалить данные
        """
        try:
            logger.info(f"Удаляю данные из КЭШа по ключу: {key}")
            self.redis.delete(key)
        except Exception as _ex:
            logger.error(f"Не удалось удалить данные из КЭШа по ключу: {key}")


if __name__ == '__main__':
    obj = Redis()
