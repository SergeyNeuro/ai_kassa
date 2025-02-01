import subprocess
import logging
from typing import Optional
import os


logger = logging.getLogger(f"app.{__name__}")
app_dir = os.path.join(os.path.dirname(__file__))
# pilot_path = os.path.join('pay', 'sber_pay', 'sb_pilot')

class SberPayManager:
    """Объект для взаимодействия с платежным терминалом Сбербанка"""

    def pay(self, value: int) -> bool:
        """Отправка счета на оплату на платежный терминал
        Args:
            value: сумма на оплату в копейках
        """
        data = self.run_command(command=['./sb_pilot', '1', str(value)])
        # data = self.run_command(command=['./' + pilot_path, '1', str(value)])
        if data == 0:
            logger.info(f"Оплата на сумму: {value} в <Сбербанк> успешно проведена")
            return True
        else:
            logger.error(f"Ошибка при оплате суммы: {value} <Сбербанк> -> {data}")
            return False

    def close_shift(self) -> bool:
        """Закрытие смены, чтобы средства поступили на расчетный счёт"""
        data = self.run_command(command=['./sb_pilot', '7'])
        if data == 0:
            logger.info("Смена <Сбербанка> успешно закрыта")
            return True
        else:
            logger.error(f"Ошибка связи с банком <Сбербанк> -> {data}")
            return False

    def check_connection(self) -> bool:
        """Проверка связи терминала с банком"""
        data = self.run_command(command=['./sb_pilot', '47', '2'])
        if data == 0:
            logger.info("Связь с банком <Сбербанк> успешна установлена")
            return True
        else:
            logger.error(f"Ошибка связи с банком <Сбербанк> -> {data}")
            return False

    @staticmethod
    def run_command(command: list) -> Optional[int]:
        """Отправка команды на платежный терминал. Базовый метод.
        Args:
            command: команда отправляемая на платежный терминал
        """
        try:
            logger.info(f"Отправляю команду на платежный терминал Сбербанка: {command}")
            result = subprocess.run(command, capture_output=True, text=True, cwd=app_dir)
            logger.info(f"Результат операции: {command} = {result}")
            result_code = int(result.stdout.split(":")[-1].strip())
            if result_code == 0:
                logger.info(f"Команда <{command}> отправленная платежному терминалу Сбербанка успешна")
                return 0
            else:
                logger.error(f"Ошибка при отправке команды {command} на платежный терминал Сбербанка. Код: {result_code}")
                return result_code
        except Exception as _ex:
            logger.critical(f"Ошибка при отправке команды <{command}> на платежный терминал Сбербанка -> {_ex}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
    obj = SberPayManager()
    obj.pay(100)
