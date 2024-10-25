import sys
import os

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QMessageBox
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


# Функция сохранения фото, на вход принимает объект класса и имя папки, куда будет сохранено фото
def photo_save(self, name_folder):
    os.makedirs(name_folder, exist_ok=True)
    existing_photos = [filename for filename in os.listdir(name_folder) if filename.startswith("photo_")]
    # Извлекаем номера фотографий и определяем следующий номер для новой фотографии
    numbers = []
    for photo in existing_photos:
        try:
            # Предполагаем, что имена файлов имеют формат "photo_номер.jpg"
            # И получаем номер, беря вторую часть имени файла
            number = int(photo.split("_")[1].split(".")[0])
            numbers.append(number)
        except (IndexError, ValueError):
            # Если возникает ошибка, просто пропускаем файл
            print(f"Не удалось извлечь номер из файла: {photo}")

    # Определяем следующий номер фотографии
    next_num = max(numbers, default=0) + 1
    # next_num = max([int(photo.split("_")[1].split(".")[0]) for photo in existing_photos], default=0) + 1

    ret, frame = self.capture.read()
    if ret:
        photo_path = os.path.join(name_folder, f"photo_{next_num}.jpg")
        cv2.imwrite(photo_path, frame)
        upload_image(photo_path)
        # QMessageBox.information(self, "Уведомление", f"Фото сохранено в папку {name_folder} с под именем photo_{next_num}")
        try:
            os.remove(photo_path)  # Вызываем функцию os.remove(), передавая ей путь к файлу.
            print(
                f"Файл '{photo_path}' успешно удален.")  # Если удаление прошло успешно, выводим соответствующее сообщение.

        except FileNotFoundError:
            print(f"Ошибка: Файл '{photo_path}' не найден.")  # Если файл не существует, выводим сообщение об ошибке.
        except PermissionError:
            print(
                f"Ошибка: У вас нет прав для удаления файла '{photo_path}'.")  # Если нет прав доступа, выводим сообщение об ошибке.
        except Exception as e:
            print(f"Произошла неожиданная ошибка: {e}")  # Ловим любые другие исключения и выводим сообщение об ошибке.
        QMessageBox.information(self, "Уведомление", f"Фото зафиксировано")


def upload_image(file_path):
    """
    Функция для загрузки изображения на API.

    :param file_path: Путь к изображению, которое нужно загрузить
    :return: Ответ от API
    """

    # URL нашего API для загрузки изображения
    url = "http://45.146.165.98:8000/upload/"

    # Открываем файл в режиме бинарного чтения
    with open(file_path, 'rb') as image_file:
        # Создаем словарь с файлом для POST-запроса
        files = {"file": image_file}

        # Отправляем POST-запрос
        response = requests.post(url, files=files)

    return response.json()


def photo_save_auto(self, name_folder):
    os.makedirs(name_folder, exist_ok=True)
    existing_photos = [filename for filename in os.listdir(name_folder) if filename.startswith("photo_")]

    next_num = max([int(photo.split("_")[1].split(".")[0]) for photo in existing_photos], default=0) + 1

    ret, frame = self.capture.read()
    if ret:
        photo_path = os.path.join(name_folder, f"photo_{next_num}.jpg")
        cv2.imwrite(photo_path, frame)
        print(f"Фото сохранено в папку {name_folder} с под именем photo_{next_num}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Детекция дефектов")
        self.setGeometry(0, 0, 640, 640)  # Установим размер окна на весь экран

        self.video_label = QLabel(self)
        self.video_label.setGeometry(0, 0, 1280, 640)  # Зададим размер видео-потока
        self.video_label.setStyleSheet("background-color: black")
        self.video_label.show()

        self.btn4 = QPushButton("Сделать фото", self)
        self.btn4.setGeometry(820, 10, 120, 78)
        self.btn4.clicked.connect(self.take_photo1)

        self.exit_btn = QPushButton("Выход", self)
        self.exit_btn.setGeometry(820, 450, 120, 78)
        self.exit_btn.clicked.connect(QApplication.quit)

        # Создаем объект cv2.VideoCapture один раз
        self.capture = cv2.VideoCapture(0)
        self.video_writer = None
        self.recording = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(0)  # Устанавливаем таймер обновления кадров на 50 мс

    def start_video(self):
        self.recording = True
        codec = cv2.VideoWriter_fourcc(*'XVID')
        folder_path = "video_show"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        existing_files = os.listdir(folder_path)
        file_number = len(existing_files) + 1
        output_file = f"video_{file_number}.mp4"
        frame_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.video_writer = cv2.VideoWriter(os.path.join(folder_path, output_file), codec, 30.0,
                                            (frame_width, frame_height))

        self.btn5.setDisabled(True)
        self.btn6.setEnabled(True)

    def stop_video(self):
        self.recording = False
        self.video_writer.release()  # Освобождаем ресурсы видео_writer
        self.btn5.setEnabled(True)
        self.btn6.setDisabled(True)

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            if self.recording:
                self.video_writer.write(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
            pix_map = QPixmap.fromImage(img)
            # pix_map = pix_map.scaled(1920, 1280, Qt.AspectRatioMode.KeepAspectRatio)
            pix_map = pix_map.scaled(frame.shape[0], frame.shape[1], Qt.AspectRatioMode.KeepAspectRatio)
            self.video_label.setPixmap(pix_map)

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
        self.photo_save("dataset")

    def closeEvent(self, event):
        # Освобождаем все ресурсы
        self.timer.stop()
        if self.video_writer is not None:
            self.video_writer.release()
        if self.capture is not None:
            self.capture.release()
        event.accept()

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
            print(type(resized_frame))

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

                # Сохраняем изображение в байтовый поток
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='JPEG')
                img_byte_arr.seek(0)  # Перемещаем указатель в начало потока

            print(f"Отправляю файл на по адресу: {url}")

            response = requests.post(
                url=f"{url}/api/dataset/upload",
                files={"file": img_byte_arr},
                params={"menu_id": menu_id},
                headers={
                    "AuthToken": TOKEN,

                }
            )
            print(f"Пришел ответ от сервера: {response.json()}")
            if response.json()["success"]:
                message = "Фотографий успешно сохранена на сервере"
            else:
                message = "Не удалось сохранить фотографию на сервере"
            QMessageBox.information(self, "Уведомление", message)
        except Exception as _ex:
            print(f"Ошибка при отправке фотографии на сервер -> {_ex}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())