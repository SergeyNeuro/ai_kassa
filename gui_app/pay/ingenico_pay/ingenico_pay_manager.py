import logging
from typing import List, Union
import subprocess
import os
import stat

from .codes import RES_CODES
from schemas import OperationSchem
from devices import DeviceChecker

# from pydantic import BaseModel

# class OperationSchem(BaseModel):
#     success: bool
#     info: str


logger = logging.getLogger(f"app.{__name__}")
app_dir = os.path.join(os.path.dirname(__file__))


class IngenicoPay:
    """Класс для взаимодействия с платежными терминалами ingenico"""
    checker = DeviceChecker()

    def init(self):
        """
        Инициализируем платежный терминал. 
        - проверяем соединение
        - проверяем соединение с банком
        - закрываем смену
        """
        # определяем порт на которому подключен терминал
        port = self.checker.get_device(device_name="Sagem")
        if not port:
            return OperationSchem(success=False, info="Нет связи с терминалом")
        else:
            self.update_port(port)

        ping = self.ping_terminal()
        if not ping.success:
            return ping
        connect = self.check_connection()
        return connect

    def update_port(self, port: str):
        """Поменяем порт в файле cashreg.ini"""
        with open(f'{app_dir}/cashreg.ini', "r") as file:
            lines = file.readlines()
        
        with open(f'{app_dir}/cashreg.ini', "w") as file:
            for line in lines:
                # Заменяем строку, начинающуюся с "PORT=" на нужное значение
                if line.startswith("PORT="):
                    file.write(f"PORT={port}\n")
                else:
                    file.write(line)

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


# Необходимые библиотеки
# sudo apt-get update
# sudo apt-get install libc6:i386
# sudo apt-get install lib32ncurses6
# sudo apt-get install lib32z1 lib32ncurses6 lib32stdc++6
# sudo chmod 666 /dev/ttyACM0
# sudo nano /etc/udev/rules.d/99-ttyACM.rules
# SUBSYSTEM=="tty", KERNEL=="ttyACM*", MODE="0666"
# sudo udevadm control --reload
# ls -l /dev/ttyACM0 ==  crw-rw-rw-

