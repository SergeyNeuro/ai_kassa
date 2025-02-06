from typing import Callable, Optional, List
import json
import logging

from libfptr10 import IFptr

# from schemas import DishSchem
# from devices import DeviceChecker

class DishSchem:
    pass


logger = logging.getLogger(f"app.{__name__}")


class Atol:
    atol: IFptr
    # checker = DeviceChecker()

    def __init__(self, settings_com_file):
        logger.info(f'Инициализирую кассу ATOL')
        self.init(settings_com_file=settings_com_file)

    def init(self, settings_com_file) -> bool:
        """Иницифлизация объекта класса для взаимодействия с кассовым аппататом Atol"""
        # создаем объект класса
        self.atol = IFptr("")

        # port = self.checker.get_device(device_name="Audioengine")
        # if not port:
        #     return False
        
        # logger.info(f"Нашел порт от устройства: {port}")

        # применяем настройки к объекту класса
        self.atol.setSettings(
            {
                IFptr.LIBFPTR_SETTING_MODEL: IFptr.LIBFPTR_MODEL_ATOL_AUTO,
                IFptr.LIBFPTR_SETTING_PORT: IFptr.LIBFPTR_PORT_USB,
                # IFptr.LIBFPTR_SETTING_COM_FILE: port,
                IFptr.LIBFPTR_SETTING_COM_FILE: settings_com_file,
                IFptr.LIBFPTR_SETTING_BAUDRATE: IFptr.LIBFPTR_PORT_BR_115200
            }
        )

        logger.info(f"Create object for connect ATOL kassa. Driver version: {self.atol.version()}")
        
        self.execute(self.close_shift)

        return True
    
    def prin_docs_from_db(self, start = 1, end = 10):
        data = {
            "type": "reportOfdExchangeStatus"
        }
        data = json.dumps(data)
        name = "check_connection"
        validate = self.validate_json_cmd(name=name, data=data)
        if validate:
            execute = self.process_json_cmd(name=name, data=data)
            return execute
        return False
    
    def get_x_report(self):
        data = {"type": "reportX"}
        data = json.dumps(data)
        name = "check_connection"
        validate = self.validate_json_cmd(name=name, data=data)
        if validate:
            execute = self.process_json_cmd(name=name, data=data)
            return execute
        return False

    def execute(self, command_func: Callable, args: Optional[tuple] = None) -> bool:
        """Базовый метод выполнения команд в системе Atol
        Args:
            command_func: команда выполняющая на кассе
            args: аргументы, которые передаются в команду
        """
        # открываем соединение
        connect = self.atol.open()
        if connect == 0:
            try:
                if args:
                    return command_func(*args)
                else:
                    return command_func()
            except Exception as _ex:
                logger.error(f"Ошибка при выполнении команды в терминале ATOL. Command: {command_func}, args: {args} -> {_ex}")
                return False
            finally:
                # закрываем соединение
                self.atol.close()
        else:
            logger.error(f"Не удалось создать соединение с ATOL. Command: {command_func}, args: {args}")
            return False

    def check_connection(self) -> bool:
        """Проверяем есть ли связь с сервером"""
        logger.info(f"Проверяю связь с банком у кассы Atol")
        data = {"type": "pingIsm"}
        data = json.dumps(data)
        name = "check_connection"
        validate = self.validate_json_cmd(name=name, data=data)
        if validate:
            execute = self.process_json_cmd(name=name, data=data)
            return execute
        return False

    def close_shift(self) -> bool:
        logger.info(f"Закрываю смену")
        data = {
            "type": "closeShift",
            "operator": {
                "name": "Иванов"
            },
            "electronically": True
        }
        data = json.dumps(data)
        name = "close_shift"
        validate = self.validate_json_cmd(name=name, data=data)
        if validate:
            execute = self.process_json_cmd(name=name, data=data)
            return execute
        return False

    def validate_json_cmd(self, name: str, data: str) -> bool:
        """Проверяем на валидность данные которые будут отправлены на запрос
        Args:
            name: наименование команды
            data: JSON строка с параметрами команды
        """
        # добавляем параметры
        self.atol.setParam(self.atol.LIBFPTR_PARAM_JSON_DATA, data)
        res = self.atol.validateJson()
        if res == 0:
            logger.info(f"Валидация команды: {name} с параметрами: {data} прошла успешно")
            return True
        else:
            logger.error(f"Ошибка при валидации команды: {name} c параметрами: {data}. "
                  f"Код ошибки: {self.atol.errorCode()}. Описание ошибки: {self.atol.errorDescription()}")
            return False

    def process_json_cmd(self, name: str, data: str):
        """Выполнение JSON команды
        Args:
            name: наименование команды
            data: JSON строка с параметрами команды
        """
        # добавляем параметры
        self.atol.setParam(self.atol.LIBFPTR_PARAM_JSON_DATA, data)
        res = self.atol.processJson()
        if res == 0:
            logger.info(f"Команда: {name} с параметрами: {data} успешно выполнена")
            return True
        else:
            logger.error(f"Ошибка при выполнении команды: {name} c параметрами: {data}. "
                  f"Код ошибки: {self.atol.errorCode()}. Описание ошибки: {self.atol.errorDescription()}")
            return False

    def create_check(self, items_list: List[DishSchem]) -> bool:
        total_price = 0
        items = []  # список с блюдами и их стоимостью
        for item in items_list:
            items.append(
                {
                    "type": "position",
                    "name": item.name,
                    "price": item.price / item.count,
                    "quantity": item.count,
                    "amount": item.price,
                    "tax": {
                        "type": "vat20"
                    }
                }
            )
            total_price += item.price
        data = {
            "type": "sell",
            "items": items,
            "payments": [
                {
                    "type": "electronically",
                    "sum": total_price
                }
            ]
        }
        name = "create_check"
        data = json.dumps(data)

        validate = self.validate_json_cmd(name=name, data=data)
        if validate:
            return self.process_json_cmd(name=name, data=data)
        return False


if __name__ == '__main__':
    obj = Atol(settings_com_file="/dev/ttyACM0")
    # obj.init()

    # obj.execute(obj.create_check, (1,))
    # obj.execute(command_func=obj.close_shift)
    obj.execute(obj.prin_docs_from_db)
