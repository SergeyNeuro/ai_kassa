from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QMessageBox, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np
from config import HEIGHT, WIDTH, SAVE_PHOTO
import logging
import sys

from cart import CartWindow
from web_core import TestWebCore
from web_core import WebCore

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
logger = logging.getLogger("app")

web_core = WebCore()

class MainWindow(QMainWindow):
    """Главное окно приложения"""
    def __init__(self):
        try:
            super().__init__()
            logger.info(f"Инициализирую главное окно")

            self.setWindowTitle("Главное окно")
            self.setGeometry(0, 0, WIDTH, HEIGHT)

            # Создаем основной макет
            self.main_layout = QVBoxLayout()
            self.main_layout.setContentsMargins(20, 20, 20, 20)
            self.main_layout.setSpacing(10)

            # Добавляем пустой виджет сверху
            self.main_layout.addStretch()

            # Создаем горизонтальный макет для видео-потока
            self.video_layout = QHBoxLayout()
            self.video_layout.addStretch()
            self.video_label = QLabel()
            self.video_label.setStyleSheet("background-color: #73C5FC; border-radius: 10px; padding: 10px")
            self.video_label.setFixedSize(WIDTH, HEIGHT)
            self.video_label.setScaledContents(True)
            self.video_layout.addWidget(self.video_label)
            self.video_layout.addStretch()
            self.main_layout.addLayout(self.video_layout)

            # Добавляем пустой виджет снизу
            self.main_layout.addStretch()

            # Создаем горизонтальный макет для кнопок
            self.button_layout = QHBoxLayout()
            self.button_layout.setContentsMargins(0, 20, 0, 0)
            self.button_layout.setSpacing(10)

            # Создаем кнопку для сканирования фото
            self.scan_button = QPushButton("Отсканировать фото")
            self.scan_button.setStyleSheet("background-color: #73C5FC; color: #000; border-radius: 10px; padding: 10px 20px; border: 1px solid gray")
            self.scan_button.setFixedSize(int(WIDTH * 0.2), int(HEIGHT * 0.1))
            self.scan_button.clicked.connect(self.open_cart_window)
            self.button_layout.addWidget(self.scan_button)

            # Сохранить фото
            if SAVE_PHOTO == "1":
                self.scan_button = QPushButton("Сохранить фото")
                self.scan_button.setStyleSheet(
                    "background-color: #73C5FC; color: #000; border-radius: 10px; padding: 10px 20px; border: 1px solid gray")
                self.scan_button.setFixedSize(int(WIDTH * 0.2), int(HEIGHT * 0.1))
                self.scan_button.clicked.connect(self.save_dataset_proto_data)
                self.button_layout.addWidget(self.scan_button)

            # Создаем кнопку для выхода
            self.exit_button = QPushButton("Выход")
            self.exit_button.setStyleSheet("background-color: #73C5FC; color: #000; border-radius: 10px; padding: 10px 20px; border: 1px solid gray")
            self.exit_button.setFixedSize(int(WIDTH * 0.2), int(HEIGHT * 0.1))
            self.exit_button.clicked.connect(QApplication.quit)
            self.button_layout.addWidget(self.exit_button)

            # Добавляем горизонтальный макет в основной макет
            self.main_layout.addLayout(self.button_layout)
            # Устанавливаем основной макет
            self.central_widget = QWidget()
            self.central_widget.setLayout(self.main_layout)
            self.setCentralWidget(self.central_widget)
            self.setStyleSheet("background-color: #FFFFFF;")

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
                pix_map = pix_map.scaled(self.video_label.width(), self.video_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
                self.video_label.setPixmap(pix_map)
        except Exception as _ex:
            logger.error(f"Ошибка при обновлении изображения с камеры -> {_ex}")

    def open_cart_window(self, checked):
        """Открываем новое окно корзины"""
        logger.info("Открываю корзину")
        ret, frame = self.capture.read()
        # frame = cv2.imread("dron.jpg")
        resized_frame = cv2.resize(frame, (640, 640))

        # отправляем изображение на сервер чтобы найти на нем блюда
        dishes_data = self.get_predict_data(image=resized_frame)
        if not dishes_data:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Ошибка")
            msg_box.setText("Не удалось распознать блюда. Повторите попытку")

            # Устанавливаем стиль для изменения цвета текста и фона
            msg_box.setStyleSheet("QMessageBox { background-color: white; }"
                                  "QLabel { color: black; }"
                                  "QPushButton { color: white; background-color: gray; }")  # Цвет текста и фона кнопок

            # Добавляем кнопки
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            msg_box.exec()  # Отображаем сообщение
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

    def save_dataset_proto_data(self) -> None:
        """Данный метод сохраняет фото на удаленном севере
        Args:
            image: изображение в формате массива numpy
        """
        ret, frame = self.capture.read()
        # frame = cv2.imread("dron.jpg")
        resized_frame = cv2.resize(frame, (640, 640))

        result = web_core.send_dataset_photo(image=resized_frame)
        if result:
            QMessageBox.information(self, "Информация", f"Фото успешно сохранено")
        else:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить фото")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()