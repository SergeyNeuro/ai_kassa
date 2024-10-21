"""
Модуль для запуска приложения с графическим интерфейсом, который
установлен на мини компьютере (например RastberryPi или RepkaPi)
"""

import sys
import os

from PyQt6.QtCore import QTimer, Qt, QPropertyAnimation, QRect
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox 
import cv2
from dotenv import load_dotenv
import requests
from PIL import Image
from io import BytesIO


load_dotenv()


WEB_SERVER_URL = os.getenv("WEB_SERVER_URL")
MENU_ID = os.getenv("MENU_ID")
TOKEN = os.getenv("TOKEN")
SAVE_PHOTO = os.getenv("SAVE_PHOTO")


def photo_save(self, name_folder):
    os.makedirs(f"{name_folder}", exist_ok=True)
    existing_photos = [filename for filename in os.listdir(name_folder) if filename.startswith("photo_")]

    if existing_photos:
        # Находим максимальный номер существующих фото
        max_num = max(int(photo.split("_")[1].split(".")[0]) for photo in existing_photos)
        next_num = max_num + 1
    else:
        next_num = 1
    new_width = 1980
    new_height = 1080

    self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, new_width)
    self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, new_height)

    ret, frame = self.capture.read()
    if ret:
        photo_path = f"{name_folder}/photo_{next_num}.jpg"
        cv2.imwrite(photo_path, frame)
        print(f"Фото сохранено в папку {name_folder} с под именем photo_{next_num}")
        message = f"Фото сохранено в папку {name_folder} с под именем photo_{next_num}"
        QMessageBox.information(self, "Уведомление", message)

def photo_save_auto(self, name_folder):
    os.makedirs(f"{name_folder}", exist_ok=True)
    existing_photos = [filename for filename in os.listdir(name_folder) if filename.startswith("photo_")]

    if existing_photos:
        # Находим максимальный номер существующих фото
        max_num = max(int(photo.split("_")[1].split(".")[0]) for photo in existing_photos)
        next_num = max_num + 1
    else:
        next_num = 1
    new_width = 1980
    new_height = 1080

    self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, new_width)
    self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, new_height)

    ret, frame = self.capture.read()
    if ret:
        photo_path = f"{name_folder}/photo_{next_num}.jpg"
        cv2.imwrite(photo_path, frame)
        print(f"Фото сохранено в папку {name_folder} с под именем photo_{next_num}")
        #message = f"Фото сохранено в папку {name_folder} с под именем photo_{next_num}"
        #QMessageBox.information(self, "Уведомление", message)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Камера и кнопки")
        self.setGeometry(0, 0, 1980, 1080)  # Установим размер окна на весь экран

        self.video_label = QLabel(self)
        #self.video_label.setGeometry(0, 0, 1280, 1080)  # Зададим размер видео-потока
        self.video_label.setGeometry(0, 0, 1980, 1080)  # Зададим размер видео-потока
        self.video_label.setStyleSheet("background-color: black")
        self.video_label.show()

        self.btn1 = QPushButton("Start_auto_photo", self)
        self.btn1.setGeometry(1290, 0, 110, 30)
        self.btn1.clicked.connect(self.take_auto_photos)

        self.btn2 = QPushButton("Stop_auto_photo", self)
        self.btn2.setGeometry(1410, 0, 110, 30)
        self.btn2.clicked.connect(self.stop_auto_photos)

        self.btn3 = QPushButton("Дефект №1", self)
        self.btn3.setGeometry(1290, 40, 110, 30)
        self.btn3.clicked.connect(self.take_photo1)

        self.btn4 = QPushButton("Дефект №2", self)
        self.btn4.setGeometry(1410, 40, 110, 30)
        self.btn4.clicked.connect(self.take_photo2)

        self.exit_btn = QPushButton("Выход", self)
        self.exit_btn.setGeometry(1290, 200, 200, 40)
        self.exit_btn.clicked.connect(QApplication.quit)

        # Виджет всплывающего окна
        #self.notification_label = QLabel(self)
        #self.notification_label.setGeometry(10, self.height() - 60, 400, 50)
        #self.notification_label.setStyleSheet("background-color: rgba(0, 0, 0, 0.7); color: white; padding: 10px; font-size: 16px")

        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(50)

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
            #image = QImage(frame, 1920, 1080, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            pixmap_resized = pixmap.scaled(self.video_label.size(), aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
            self.video_label.setPixmap(pixmap_resized)

    def take_auto_photos(self):
        # Код для автоматического снятия фото каждую секунду
        self.auto_photo_timer = QTimer(self)
        self.auto_photo_timer.timeout.connect(self.capture_and_save_photo)
        self.auto_photo_timer.start(5000)  # 5 секунд

    def stop_auto_photos(self):
        self.auto_photo_timer.stop()

    def capture_and_save_photo(self):
        photo_save_auto(self, "auto_photo")
        
    def take_photo1(self):
        self.photo_save("num_1")

    def take_photo2(self):
        self.photo_save("num_2")

    def exit_application(self):
        self.timer.stop()
        self.capture.release()
        self.close()

    def photo_save(self, name_folder):
        os.makedirs(f"{name_folder}", exist_ok=True)
        existing_photos = [filename for filename in os.listdir(name_folder) if filename.startswith("photo_")]

        if existing_photos:
            # Находим максимальный номер существующих фото
            max_num = max(int(photo.split("_")[1].split(".")[0]) for photo in existing_photos)
            next_num = max_num + 1
        else:
            next_num = 1
        new_width = 640
        new_height = 640

        ret, frame = self.capture.read()
        if ret:
            # Изменяем размер изображения до 640x640
            resized_frame = cv2.resize(frame, (new_width, new_height))

            photo_path = f"{name_folder}/photo_{next_num}.jpg"
            cv2.imwrite(photo_path, resized_frame)
            print(f"Фото сохранено в папку {name_folder} с под именем photo_{next_num}")
            message = f"Фото сохранено в папку {name_folder} с под именем photo_{next_num}"
            QMessageBox.information(self, "Уведомление", message)

            if int(SAVE_PHOTO) == 1:
                self.send_photo(photo_path=photo_path)

    def send_photo(
            self,
            photo_path: str,
            menu_id: int = int(MENU_ID),
            url: str = WEB_SERVER_URL
    ) -> None:
        """Метод для отправки фотографии на удаленный сервер
        Args:
            photo_path: путь до фотографии
            menu_id: идентификатор меню, к которому относится отправляемое блюдо
            url: адрес куда нужно отправлять фотографию
        """
        try:
            print(f"Открываю файл: {photo_path} и меняю размер на 640x640")
            with Image.open(photo_path) as img:
                # img = img.resize((640, 640))

                # Сохраняем изображение в байтовый поток
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='JPEG')
                img_byte_arr.seek(0)  # Перемещаем указатель в начало потока

            print(f"Отправляю файл на по адресу: {url}")

            print(TOKEN)

            response = requests.post(
                url=f"{url}/api/dataset/upload",
                files={"file": img_byte_arr},
                params={"menu_id": menu_id},
                headers={"auth_token": TOKEN}
            )
            print(f"Пришел ответ от сервера: {response.json()}")
        except Exception as _ex:
            print(f"Ошибка при отправке фотографии на сервер -> {_ex}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())