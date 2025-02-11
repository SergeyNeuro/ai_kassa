import subprocess
import threading
import time
import os
import logging

from devices import DeviceChecker

logger = logging.getLogger(f"app.{__name__}")


class BarcodeScanner:
    device_checker = DeviceChecker()

    def __init__(self, port: str = "/dev/ttyACM0"):
        self.port = port
        self.scan_flag = False
        self.process = None
        self.scan_thread = None

        # инициализируем объект класса
        self.init()

    def init(self):
        device_port = self.device_checker.get_device("Metrologic Instruments")
        logger.info(f"Порт barcode сканера: {device_port}")
        self.port = device_port

    def run_scanner(self) -> str:
        """Сканируем пока не получим значение"""
        self.scan_flag = True
        self.process = subprocess.Popen(['cat', self.port], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while self.scan_flag:
            output = self.process.stdout.readline()
            # сканиурем до получения значение
            if output:
                output = output.decode('utf-8').strip()
                print(f"Received: {output}")
                # Останавливаем сканирование, если получено значение
                self.stop_scanner()
                return output  # Возвращаем полученное значение

    def stop_scanner(self):
        """Останавливает сканирование."""
        if self.scan_flag:
            self.scan_flag = False
            if self.process:
                self.process.terminate()
                self.process.wait()
            print("Scanning stopped.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
    # # Пример использования
    scanner = BarcodeScanner()
    #
    # # Запуск сканирования в отдельном потоке
    # scan_thread = threading.Thread(target=scanner.run_scanner)
    # scan_thread.start()
    #
    # # # Остановка сканирования через 10 секунд (пример)
    # # import time
    # #
    # # time.sleep(10)
    # # scanner.stop_scanner()
    # #
    # # # Ожидание завершения потока
    # # scan_thread.join()
    # # print("Scanning process finished.")