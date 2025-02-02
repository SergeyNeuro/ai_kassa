import pyudev
from typing import Union
import logging

logger = logging.getLogger(f"app.{__name__}")


class DeviceChecker:
    """Класс с методами для опеределения какие устройства
    присоединены к каждому порту устройства
    """

    def get_device(self, device_name: str, ports: int = 10, check = False) -> Union[str, None]:
        """Проходимся по списку портов и определяем на каком
        именно закреплен нужное нам устройство
        Args:
            device_name: наименование устройства которое мы ищем
            range: кол-во портов по которым проходимся за информацией
            check: флаг. Если True, то мы просто смотрим какие устройства находятся на портах
        """
        logger.info(f"Ищу на какому порту находится устройство: {device_name}")
        for i in range(ports):
            res = self.check_device_by_port(device_name=device_name, port=f"ttyACM{i}", check=check)
            if res:
                return res

        logger.error(f"Устройство: {device_name} не найдено на портах")


    def check_device_by_port(self, device_name: str, port: str = "ttyACM0", check = False) -> Union[str, None]:
        """Определяем какое устройство на порту по его имени
        Args:
            device_name: наименование устройства порт коорого ищем
            port: порт который проверяется
            check: флаг который используется чтобы просто проверить какие устройства находятся на портах

        """
        logger.info(f"Проверяю на находится ли устройство: {device_name} на порту: {port}")
        context = pyudev.Context()
        devices = context.list_devices(subsystem='tty')

        for device in devices:
            if device.device_node.endswith(port):
                if not check:
                    if device.get('ID_VENDOR_FROM_DATABASE', None) == device_name:
                        logger.info(f"Устройство: {device_name} найдено на порту: {device.device_node}")
                        return device.device_node
                else:
                    print(f"Устройство на порту {port}:")
                    print(f"  Имя устройства: {device.device_node}")
                    print(f"  Производитель: {device.get('ID_VENDOR_FROM_DATABASE', 'Неизвестно')}")
                    print(f"  Модель: {device.get('ID_MODEL_FROM_DATABASE', 'Неизвестно')}")
                    print(f"  Серийный номер: {device.get('ID_SERIAL_SHORT', 'Неизвестно')}")
                    print(f"  VID:PID: {device.get('ID_VENDOR_ID')}:{device.get('ID_MODEL_ID')}")
                    print()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")

    kassa = "Audioengine"
    terminal = "Sagem"
    obj = DeviceChecker()
    device = obj.get_device(device_name=kassa)