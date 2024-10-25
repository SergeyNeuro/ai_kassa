import sys
import logging

from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np

from cart import CartWindow
from web_core import WebCore, TestWebCore

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
logger = logging.getLogger("app")


# web_core = TestWebCore()
web_core = WebCore()


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    def __init__(self):
        try:
            super().__init__()
            logger.info(f"Инициализирую главное окно")

            self.setWindowTitle("Главное окно")
            self.setGeometry(0, 0, 640, 640)

            self.video_label = QLabel(self)
            self.video_label.setGeometry(0, 0, 1280, 640)  # Зададим размер видео-потока
            self.video_label.setStyleSheet("background-color: black")
            self.video_label.show()

            self.btn4 = QPushButton("Отсканировать фото", self)
            self.btn4.setGeometry(820, 10, 120, 78)
            self.btn4.clicked.connect(self.open_cart_window)

            self.exit_btn = QPushButton("Выход", self)
            self.exit_btn.setGeometry(820, 450, 120, 78)
            self.exit_btn.clicked.connect(QApplication.quit)

            # Создаем объект cv2.VideoCapture один раз
            self.capture = cv2.VideoCapture(0)
            self.video_writer = None
            self.recording = False

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(50)  # Устанавливаем таймер обновления кадров на 50 мс
        except Exception as _ex:
            logger.error(f"Ошибка при создании главного окна -> {_ex}")

    def update_frame(self):
        """Метод обновления изображения с камеры"""
        try:
            ret, frame = self.capture.read()
            if ret:
                if self.recording:
                    self.video_writer.write(frame)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
                pix_map = QPixmap.fromImage(img)
                pix_map = pix_map.scaled(frame.shape[0], frame.shape[1], Qt.AspectRatioMode.KeepAspectRatio)
                self.video_label.setPixmap(pix_map)
        except Exception as _ex:
            logger.error(f"Ошибка при обновлении изображения с камеры -> {_ex}")

    def open_cart_window(self, checked):
        """Открываем новое окно корзины"""
        logger.info("Открываю корзину")
        ret, frame = self.capture.read()
        resized_frame = cv2.resize(frame, (640, 640))

        # отправляем изображение на сервер чтобы найти на нем блюда
        dishes_data = self.get_predict_data(image=resized_frame)
        if not dishes_data:
            QMessageBox.information(self, "Ошибка", "Не удалось распознать блюда. Повторите попытку")
        else:
            self.w = CartWindow(image=resized_frame, dishes_data=dishes_data)
            self.w.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            self.w.show()
            self.setDisabled(True)
            self.w.closeEvent = self.close_cart_window

    def close_cart_window(self, event):
        """Разблокируем главное окно при закрытии корзины"""
        self.setDisabled(False)  # Разблокируем главное окно
        event.accept()  # Принять событие закрытия

    def get_predict_data(self, image: np.ndarray) -> list:
        """Данный метод отправляет данные для предсказания блюд на фото
        Args:
            image: изображение в формате массива numpy
        """
        return web_core.send_image_to_predict(image=image)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()