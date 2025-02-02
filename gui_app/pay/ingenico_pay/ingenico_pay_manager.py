import logging
from typing import List, Union
import subprocess
import os

from .codes import RES_CODES
from schemas import OperationSchem

logger = logging.getLogger(f"app.{__name__}")
app_dir = os.path.join(os.path.dirname(__file__))


class IngenicoPay:
    """Класс для взаимодействия с платежными терминалами ingenico"""


    def pay(self, value: int) -> OperationSchem:
        """Отправка команды на плату
        Args:
            value: сумма на оплату в копейках
        """
        cmd_name = "Pay"
        res = self.run_command(command=["./cashreg", "/o1", f"/a{value}"], cmd_name=cmd_name)

        if res == "000":
            return OperationSchem(success=True, info="Оплата успешна")
        else:
            return OperationSchem(success=False, info=RES_CODES[res])

    def check_connection(self) -> OperationSchem:
        """Команда для проверки соединения с терминала с банком
        """
        cmd_name = "Ping host"
        res = self.run_command(command=["./cashreg", "/o95"], cmd_name=cmd_name)

        if res == "000":
            return OperationSchem(success=True, info="Проверка связи с банком успешна")
        else:
            return OperationSchem(success=False, info=RES_CODES[res])

    def ping_terminal(self) -> OperationSchem:
        """Команда для проверки соединения с терминалом
        :return True или False в зависимости от того, успешна ли команда или нет
        """
        cmd_name = "Ping terminal"
        res = self.run_command(command=["./cashreg", "/o201"], cmd_name=cmd_name)

        if res == "000":
            return OperationSchem(success=True, info="Проверка связи с терминалом успешна")
        else:
            return OperationSchem(success=False, info=RES_CODES[res])

    def run_command(self, command: List[str], cmd_name: str = "test") -> str:
        """Базовый метод выполнения команды
        Args:
            command: команда которую требуется отправить на терминал в виде списка
            cmd_name: наименование команды (для визуализации
        """
        logger.info(f"Пришел запрос на выполнение команды {cmd_name}: {command}")
        subprocess.run(command, capture_output=True, text=True, cwd=app_dir)     # непосредственно выполнение самой команды

        res = self.get_cmd_res(cmd_name=cmd_name)

        logger.info(f"Код выполнения команды {cmd_name}: {res}. Расшифровка -> {RES_CODES[res]}")

        return res

    @staticmethod
    def get_cmd_res(cmd_name: str = "test") -> Union[str, None]:
        """Открываем файл output.out и смотрим на результат операции
        Args:
            cmd_name: наименование команды которая выполнялась (используется для визуализации кода)
        """
        try:
            logger.info(f"Пришел запрос на извлечении результата выполнения команды: {cmd_name}")

            # Открываем файл для чтения
            with open(f'{app_dir}/output.out', 'r') as file:
                # Читаем первые 3 символа из файла (код ответа состоит из 3-х символов)
                value = file.read(3)

            logger.debug(f"Код выполнения команды {cmd_name}: {value}")

            return value
        except Exception as _ex:
            logger.error(f"Ошибка при чтении результата выполнения команды: {cmd_name} -> {_ex}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
    obj = IngenicoPay()
    print(obj.ping_terminal())
    # print(obj.check_connection())
    # print(obj.pay(value=1000))
