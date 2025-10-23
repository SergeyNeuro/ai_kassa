"""Данный метод служит для Type[BaseModel] выбора системы взаимодействия с КЭШем"""

from typing import Type, Union
from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseCache(ABC):
    """Интерфейс класс предписывающий взаимодействие с КЭШем"""

    @abstractmethod
    def get_data_from_cache(self, key: str, data_class: Type[BaseModel]) -> Union[Type[BaseModel], None]:
        """Интерфейс метод для извлечения данных из КЭШа по ключу
        Args:
            key: ключ по которому данные извлекаются из КЭШа
            data_class: объект данных в которые необходимо преобразовать
                извлеченные данные
        :return
            данные преобразованные в data_class or None
        """
        pass

    @abstractmethod
    def set_data_in_cache(self, key: str, value: BaseModel, live_time: int) -> bool:
        """Интерфейс метод который сохраняет pydantic объект в КЭШ
        Args:
            key: ключ по которому заносятся в КЭШ
            value: значение которое заносится в КЭШ
            live_time: время на которое заносятся данные в КЭШ
        :return
            True or False в зависимости удалось сохранить данные или нет
        """
        pass

    @abstractmethod
    def set_single_data_in_cache(
            self,
            key: str,
            value: Union[int, str, bool],
            live_time: int = 3500,
    ) -> None:
        pass

    @abstractmethod
    def get_single_data_from_cache(self, key: str) -> Union[int, str, bool, None]:
        """
        Метод извлекает из КЭШа json и преобразует его в pydantic объект согласно той схеме которую в него передали
        Args:
            key: (str) — Ключ по которому необходимо искать объект
        Return:
            Значение (int or str or bool) либо None
        """
        pass
