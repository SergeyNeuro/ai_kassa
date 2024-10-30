"""Модуль с корзиной по одному заказу"""
from typing import Union
import logging

from PyQt6.QtWidgets import (
    QPushButton,
    QLabel,
    QHBoxLayout,
    QWidget,
    QGridLayout,
    QMessageBox,
    QLineEdit
)
from PyQt6.QtWidgets import QFrame
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import numpy
import cv2

from config import DISTH_TYPE, COUNT_TYPE, COLORS, HEIGHT, WIDTH
from painter import Painter


logger = logging.getLogger(f"app.{__name__}")


class CartWindow(QWidget):
    """Окно корзины с изображением и кнопками"""
    def __init__(self, image: numpy.ndarray, dishes_data: list):
        super().__init__()

        # отправляем изображение на веб сервер, для предсказания какие блюда на фото
        self.dishes_data = dishes_data

        if not self.dishes_data:
            QMessageBox.information(self, "Ошибка", "Не удалось распознать блюда")

        else:
            self.image = image

            # настраиваем главное окно
            self.setWindowTitle("Корзина")
            self.setGeometry(100, 100, int(WIDTH * 0.8), int(HEIGHT * 0.6))  # Размеры окна
            self.main_layout = QHBoxLayout()

            # Изменяем фон окна и цвет текста
            self.setStyleSheet("background-color: #1b193c; color: #ffffff;")

            # Изменяем цвет текста для всех виджетов текста
            self.setStyleSheet("QLabel, QPushButton { color: #ffffff; border-bottom: 1px solid #ffffff; }")

            # Добавляем разделительную полосу между левым и правым блоком
            self.main_layout.setSpacing(10)

            # Левый виджет для изображения
            self.create_left_widget()

            # правый виджет для информации о блюдах в котором будет происходить все взаимодействие
            self.create_right_widget()

            #инициализируем главный слой
            self.setLayout(self.main_layout)

            base_layout = QGridLayout()
            right_widget = QWidget()
            right_widget.setLayout(base_layout)

    #...
            self.main_layout.addWidget(right_widget)

            # Добавляем разделительную полосу между левым и правым блоком
            line = QFrame()
            line.setFrameShape(QFrame.Shape.VLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            self.main_layout.addWidget(line)

            # Добавляем разделительные полосы между строками
            for i in range(len(self.dishes_data)):
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setFrameShadow(QFrame.Shadow.Sunken)
                base_layout.addWidget(line, i+1, 0, 1, 5)

    def pay_cart(self):
        """Проводим логику оплаты заказа"""
        logger.info("Обрабатываю ивент на оплату")
        total_price = 0
        for one_dish in self.dishes_data:
            if type(one_dish["dish_data"]) == list:
                QMessageBox.information(self, "Ошибка", "Заполнен информация не по всем блюдам")
                break
            else:
                total_price += one_dish["dish_data"]["price"]
        else:   # выполняется если цикл корректно завершился
            logger.info(f"Сумма оплаты заказа: {total_price}")
            QMessageBox.information(self, "Оплата", f"Сумма к оплате: {total_price} рублей")
            self.close()

    def create_left_widget(self):
        """Настройка левого виджета окна корзины. В левой части находится изображение
        с распознанными блюдами
        """
        # Левый виджет для изображения
        self.image_label = QLabel()
        self.set_image(self.image)
        self.main_layout.addWidget(self.image_label)
        self.setStyleSheet("background-color: #1b193c;")

    def set_image(self, image: numpy.ndarray):
        """Обрабатываем изображение и наносим на него боксы и названия блюд
        пришедшие с веб сервера
        Args:
            image: изображение в формате массива numpy
            dish_data: список словарей пришедший от веб сервера
            color: цвет которым будет блюдо обозначено на изображении в формате RGB
        """
        # Преобразуем цветовую схему с BGR на RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # рисуем на изображении квадраты с отметкой какое блюдо изображено
        for index, one_dish in enumerate(self.dishes_data):
            print(one_dish)
            Painter(
                image=image,
                top_corner=(int(one_dish["x1"]), int(one_dish["y1"])),
                bot_corner=(int(one_dish["x2"]), int(one_dish["y2"])),
                label=str(index + 1),
                color=COLORS[index]
            )

        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(q_image).scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio))

    @staticmethod
    def fill_tail_dishes_layout(layout: QGridLayout):
        font = QFont("Arial", 16)  # Установить размер шрифта
        layout.addWidget(QLabel("№", font=font), 0, 0)
        layout.addWidget(QLabel("Название", font=font), 0, 1)
        layout.addWidget(QLabel("Тип блюда", font=font), 0, 2)
        layout.addWidget(QLabel("Кол-во", font=font), 0, 3)
        layout.addWidget(QLabel("Цена, руб", font=font), 0, 4)

        # Добавляем stretch в остальные столбцы, чтобы они расширялись равномерно
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 3)
        layout.setColumnStretch(2, 2)
        layout.setColumnStretch(3, 2)
        layout.setColumnStretch(4, 2)

        # Установить минимальную ширину для первого столбца
        layout.setColumnMinimumWidth(0, 50)

    def create_right_widget(self, base_layout: QGridLayout = None):
        """Настройка правого виджета корзины, на котором будут находится
        Args:
            layout: слой на который необходимо вставлять виджеты
            base_layout: слой, на котором будет отображаться логическая информация
        """
        logger.info(f"Наполнения правого слоя")
        total_price = 0     # переменная для хранения цены всего, что находится на подносе

        if not base_layout:
            logger.info(f"Правый слой не создан. Создаю его")
            base_layout = QGridLayout()
            right_widget = QWidget()
            right_widget.setLayout(base_layout)
            right_widget.setStyleSheet("background-color: #1b193c;")



            # Добавляем разделительную линию вертикально
            line = QFrame()
            line.setFrameShape(QFrame.Shape.VLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            base_layout.addWidget(line, 0, 0, -1, 1)


            # Добавляем виджет с фиксированной шириной в качестве отступа
            spacer = QWidget()
            spacer.setFixedWidth(10)
            base_layout.addWidget(spacer, 0, 1, -1, 1)
            # Добавляем текст
            self.fill_tail_dishes_layout(layout=base_layout)

            self.main_layout.addWidget(right_widget)
        else:
            logger.info(f"Правый слой создан. Очищаю его")
            self.clear_layout(layout=base_layout)
        self.fill_tail_dishes_layout(layout=base_layout)

        for index, dish_data in enumerate(self.dishes_data):
            dish_price = self.add_one_dish_data(layout=base_layout, data=dish_data["dish_data"], index=index + 1)
            if dish_price:
                total_price += dish_price

        # показываем итоговую стоимость всего что есть на подносе
        if total_price > 0:
            base_layout.addWidget(QLabel(str(total_price)), index + 2, 4)

        # Добавляем кнопку Назад
        back_btn = QPushButton("Назад", self)
        back_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e4eafe;
                        color: #000;
                        border: none;
                        padding: 10px 20px;
                        font-size: 16px;
                        cursor: pointer;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                    }
                    QPushButton:hover {
                        background-color: #1a237e;
                    }
                    QPushButton:pressed {
                        background-color: #0d47a1;
                    }
                """)
        back_btn.clicked.connect(self.close)
        base_layout.addWidget(back_btn, index + 3, 0)

        # добавляю кнопку Оплатить
        pay_btn = QPushButton("Оплатить", self)
        pay_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e4eafe;
                        color: #000;
                        border: none;
                        padding: 10px 20px;
                        font-size: 16px;
                        cursor: pointer;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                    }
                    QPushButton:hover {
                        background-color: #1a237e;
                    }
                    QPushButton:pressed {
                        background-color: #0d47a1;
                    }
                """)
        pay_btn.clicked.connect(lambda: self.pay_cart())
        base_layout.addWidget(pay_btn, index + 3, 5)

    def add_one_dish_data(self, layout: QGridLayout, data: Union[dict, list], index: int) -> Union[int, None]:
        """Добаление на слой данных по одному блюду + реализуется логика спорных позиций
        когда на выбор блюд несколько
        Args:
            layout: слой на который нужно добавить данные о блюде
            data: данные которые нужно занести
        : return
            Стоимость блюда, если она выбрана
        """
        layout.addWidget(QLabel(str(index)), index, 0)
        if type(data) == dict:
            font = QFont("Arial", 16)  # Установить размер шрифта
            label = QLabel(str(index))
            label.setFont(font)
            layout.addWidget(label, index, 0)
            label = QLabel(data["name"])
            label.setFont(font)
            layout.addWidget(label, index, 1)
            label = QLabel(DISTH_TYPE[data["type"]])
            label.setFont(font)
            layout.addWidget(label, index, 2)
            label = QLabel(self.add_dish_count_by_type(count_type=data["count_type"], count=data["count"]))
            label.setFont(font)
            layout.addWidget(label, index, 3)
            label = QLabel(str(data["price"]))
            label.setFont(font)
            layout.addWidget(label, index, 4)
            logger.info(f"Добавляю информацию о блюде: {data}")
            layout.addWidget(QLabel(data["name"]), index, 1)    # наименование блюда
            layout.addWidget(QLabel(DISTH_TYPE[data["type"]]), index, 2)    # тип блюда
            layout.addWidget(QLabel(self.add_dish_count_by_type(count_type=data["count_type"], count=data["count"])), index, 3) # кол-во блюда
            layout.addWidget(QLabel(str(data["price"])), index, 4)  # цена блюда
            # добавляем кнопку в случае если у блюду необходимо изменить кол-во
            if data["count_type"] > 10:
                btn = QPushButton("Изменить кол-во", self)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e4eafe;
                        color: #000;
                        border: none;
                        padding: 10px 20px;
                        font-size: 16px;
                        cursor: pointer;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                    }
                    QPushButton:hover {
                        background-color: #1a237e;
                    }
                    QPushButton:pressed {
                        background-color: #0d47a1;
                    }
                """)
                btn.clicked.connect(lambda: self.create_price_dish_widget(index=index, layout=layout))
                layout.addWidget(btn, index, 5)
            return data["price"]
        else:
            if len(data) > 1:
                logger.info(f"Спорное блюдо: {data}")
                layout.addWidget(QLabel("Спорная позиция"), index, 1)
                layout.addWidget(QLabel(DISTH_TYPE[data[0]["type"]]), index, 2)
                btn = QPushButton("Выбрать блюдо", self)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e4eafe;
                        color: #000;
                        border: none;
                        padding: 10px 20px;
                        font-size: 16px;
                        cursor: pointer;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                    }
                    QPushButton:hover {
                        background-color: #1a237e;
                    }
                    QPushButton:pressed {
                        background-color: #0d47a1;
                    }
                """)
                btn.clicked.connect(lambda: self.create_changing_dish_widget(index=index, layout=layout))
                layout.addWidget(btn, index, 5)
                btn.clicked.connect(lambda: self.create_changing_dish_widget(index=index, layout=layout))
                layout.addWidget(btn, index, 5)
            else:
                # в списке спорных блюд всего 1 позиция (расцениваем как не спорную)
                self.add_one_dish_data(layout=layout, data=data[0], index=index)
                self.dishes_data[index - 1]["dish_data"] = data[0]  # преобразуем список в словарь
                return data[0]["price"]

    def add_dish_count_by_type(self, count_type: int, count: int) -> str:
        """Данный создает в зависимости от count_type (в чем измеряется блюдо) и count (его кол-ва)
        строку для отображения
        Args:
            count_type: тип измерения продукции
                (
                    1 - измеряется в порциях (неизменная, цена от кол-ва не изменяется)
                    2 - измеряется в штуках (неизменная, цена от кол-ва  не изменяется)
                    3 - измеряется по массе (неизменная, цена от кол-ва не изменяется)
                    4 - измеряется в объеме (неизменная, цена от кол-ва не изменяется)

                    11 - измеряется в порциях (необходимо кол-во для определения цены. Результат вводится вручную)
                    12 - измеряется в штуках (необходимо кол-во для определения цены. Результат вводится вручную)
                    13 - измеряется в массе (необходимо кол-во для определения цены. Результат вводится вручную)
                    14 - измеряется в объеме (необходимо кол-во для обределения цены. Результат вводится в вручную)
                )
            count: кол-во блюда
        """
        return DishCountVisual(count_type=count_type, count=count).dish_count

    def create_changing_dish_widget(self, index: int, layout: QGridLayout):
        """Создание виджетов для разрешения конфликта спорных блюд
        Args:
            index: индекс элемента в списке данных о блюдах
            layout: слой на котором необходимо отобразить новые виджеты
        """
        self.clear_layout(layout=layout)
        self.show_changing_dishes(index=index, layout=layout)

    def show_changing_dishes(self, index: int, layout: QGridLayout):
        """Отображаем список блюд между которыми нужно выбрать и определиться
        Args:
            index: индекс элемента массива который загружен в оперативную мамять
            layout: слой на котором необходимы отобразить новые виджеты
        """
        self.fill_tail_dishes_layout(layout=layout)
        for count, dish in enumerate(self.dishes_data[index - 1]["dish_data"]):
            self.create_one_dish_node(data=dish, count=count + 1, index=index - 1, layout=layout)

        # добавляем кнопку Назад
        back_btn = QPushButton("Назад", self)
        back_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e4eafe;
                        color: #000;
                        border: none;
                        padding: 10px 20px;
                        font-size: 16px;
                        cursor: pointer;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                    }
                    QPushButton:hover {
                        background-color: #1a237e;
                    }
                    QPushButton:pressed {
                        background-color: #0d47a1;
                    }
                """)
        back_btn.clicked.connect(lambda: self.back(layout=layout))
        layout.addWidget(back_btn, count + 2, 0)

    def create_one_dish_node(self, data: dict, count: int, index: int, layout: QGridLayout):
        """Добавляет на слой данные об одном спорном блюде
        Args:
            data: данные блюда
            count: счетчик добавления блюда на слой
            index: индекс элемента в основном массиве данных, который приходит при сканировании фото
            layout: слой на который добавляет блюдо
        """
        layout.addWidget(QLabel(str(count)), count, 0)
        layout.addWidget(QLabel(data["name"]), count, 1)
        layout.addWidget(QLabel(DISTH_TYPE[data["type"]]), count, 2)
        layout.addWidget(QLabel(self.add_dish_count_by_type(count_type=data["count_type"], count=data["count"])), count, 3)
        layout.addWidget(QLabel(str(data["price"])), count, 4)


        btn = QPushButton("Выбрать блюдо", self)
        btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e4eafe;
                        color: #000;
                        border: none;
                        padding: 10px 20px;
                        font-size: 16px;
                        cursor: pointer;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                    }
                    QPushButton:hover {
                        background-color: #1a237e;
                    }
                    QPushButton:pressed {
                        background-color: #0d47a1;
                    }
                """)
        btn.clicked.connect(lambda: self.choice_changing_dish(index=index, count=count - 1, layout=layout))
        layout.addWidget(btn, count, 5)

    def choice_changing_dish(self, index: int, count: int, layout: QGridLayout):
        """Функция по которой выбирается конкретное блюда из списка спорных блюд
        Args:
            index: индекс элемента из общего списка всех блюд на картинке
            count: индекс конкретного блюда из списка, который выбрал пользователь
        """
        logger.info(f"Выбираю блюдо под индексом: {count} из списка {self.dishes_data[index]['dish_data']}")
        print(self.dishes_data[index]["dish_data"][count], count)
        self.dishes_data[index]["dish_data"] = self.dishes_data[index]["dish_data"][count]
        self.create_right_widget(base_layout=layout)

    def create_price_dish_widget(self, index: int, layout: QGridLayout):
        """Создание виджетов для выбора кол-ва блюда в спорных ситуациях
        Args:
            index: индекс элемента массива который загружен в оперативную мамять
            layout: слой на котором необходимы отобразить новые виджеты
        """
        self.clear_layout(layout=layout)
        self.show_price_dish_widget(index=index - 1, layout=layout)

    def show_price_dish_widget(self, index: int, layout: QGridLayout):
        """Отображение вижетов для выбора кол-ва блюда в сорных ситуациях
        Работает по паттерну стратегия в зависимости от того, какой тип люда
        """
        logger.info(f"Добавляю информацию для ввода кол-ва блюда. index: {index}")

        data = self.dishes_data[index]["dish_data"]
        self.fill_tail_dishes_layout(layout=layout)

        # добавляем виджеты с данными о продукте
        layout.addWidget(QLabel(str(index + 1)), index + 1, 0)  # счетчик
        layout.addWidget(QLabel(data["name"]), index + 1, 1)  # наименование блюда
        layout.addWidget(QLabel(DISTH_TYPE[data["type"]]), index + 1, 2)  # тип блюда

        # вставляем поле, в котором нужно вводить кол-во блюда
        self.dish_count_edit = QLineEdit(parent=self)
        self.dish_count_edit.setPlaceholderText("Введите количество")
        self.dish_count_edit.setText(str(data["count"]))
        layout.addWidget(self.dish_count_edit, index + 1, 3)

        layout.addWidget(QLabel(COUNT_TYPE[data["count_type"]]), index + 1, 4)  # единица измерения блюда
        layout.addWidget(QLabel(str(data["price"])), index + 1, 5)  # цена блюда

        # добавляем новую переменную, которая указываем минимальное значение кол-ва блюда
        if "min_count" not in data:
            data["min_count"] = data["count"]

        # добавляем кнопку для изменения кол-ва блюда
        change_btn = QPushButton("Изменить", self)
        change_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e4eafe;
                        color: #000;
                        border: none;
                        padding: 10px 20px;
                        font-size: 16px;
                        cursor: pointer;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                    }
                    QPushButton:hover {
                        background-color: #1a237e;
                    }
                    QPushButton:pressed {
                        background-color: #0d47a1;
                    }
                """)
        change_btn.clicked.connect(lambda: self.change_dish_count(index=index, layout=layout))
        layout.addWidget(change_btn, index + 2, 5)

        # добавляем кнопку Назад
        back_btn = QPushButton("Назад", self)
        back_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e4eafe;
                        color: #000;
                        border: none;
                        padding: 10px 20px;
                        font-size: 16px;
                        cursor: pointer;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                    }
                    QPushButton:hover {
                        background-color: #1a237e;
                    }
                    QPushButton:pressed {
                        background-color: #0d47a1;
                    }
                """)
        back_btn.clicked.connect(lambda: self.back(layout=layout))
        layout.addWidget(back_btn, index + 2, 0)

    def change_dish_count(self, index: int, layout: QGridLayout):
        """Изменяем значение кол-ва блюда и производим
        пересчет его стоимости
        """
        data = self.dishes_data[index]["dish_data"]
        new_dish_text = self.dish_count_edit.text()
        try:
            new_dish_count = int(new_dish_text)
            if new_dish_count < data["min_count"]:
                raise ValueError    # вызываем ошибку, чтобы указать что было введено не корректное значение
            new_price = (new_dish_count * data["price"]) // data["count"]
            data["price"] = new_price
            data["count"] = new_dish_count
            self.create_right_widget(base_layout=layout)
        except Exception as _ex:
            QMessageBox.information(self, "Ошибка", "Введено слишком маленькое или не корректное значение")

    def back(self, layout: QGridLayout):
        """Перейти в центральное меню корзины
        Args:
            layout: слой на котором отражены все данные
        """
        self.create_right_widget(base_layout=layout)

    def clear_layout(self, layout: QGridLayout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()  # Получаем виджет
            if widget is not None:
                widget.deleteLater()  # Удаляем виджет
            layout.removeItem(layout.itemAt(i))  # Удаляем элемент из layout


class DishCountVisual:
    """Класс для визуализации данных о кол-ве блюда в зависимости от его типа и кол-ва"""
    def __init__(self, count_type: int, count: int):
        self.dish_count = self.get_visual_count_data(count_type=count_type, count=count)

    def get_visual_count_data(self, count_type: int, count: int) -> str:
        """Метод который возвращает строку о количесте блюда в зависимости от того
        в чем оно измеряется (в порциях, массе, штуках, объеме и т.п.)
        Args:
            count_type: тип измерения продукции
                (
                    1 - измеряется в порциях (неизменная, цена от кол-ва не изменяется)
                    2 - измеряется в штуках (неизменная, цена от кол-ва  не изменяется)
                    3 - измеряется по массе (неизменная, цена от кол-ва не изменяется)
                    4 - измеряется в объеме (неизменная, цена от кол-ва не изменяется)

                    11 - измеряется в порциях (необходимо кол-во для определения цены. Результат вводится вручную)
                    12 - измеряется в штуках (необходимо кол-во для определения цены. Результат вводится вручную)
                    13 - измеряется в массе (необходимо кол-во для определения цены. Результат вводится вручную)
                    14 - измеряется в объеме (необходимо кол-во для обределения цены. Результат вводится в вручную)
                )
            count: кол-во блюда
        """
        method_dict = {
            1: self.get_1_type_dish_count,
            2: self.get_2_type_dish_count,
            3: self.get_3_type_dish_count,
            4: self.get_4_type_dish_count,
            11: self.get_1_type_dish_count,
            12: self.get_2_type_dish_count,
            13: self.get_3_type_dish_count,
            14: self.get_4_type_dish_count,
        }
        return method_dict[count_type](count)

    def get_1_type_dish_count(self, count: int) -> str:
        """Возвращает визуализированные данные когда блюдо измеряется в порциях
        Args:
            count: кол-во блюда
        """
        logger.info(f"Блюдо измеряется в порциях")
        if count == 1:
            name = f"{count} порция"
        elif 2 <= count <= 4:
            name = f"{count} порции"
        else:
            name = f"{count} порций"
        return name

    def get_2_type_dish_count(self, count: int) -> str:
        """Возвращает визуализированные данные когда блюдо измеряется в штуках
        Args:
            count: кол-во блюда
        """
        logger.info(f"Блюдо измеряется в штуках")
        return f"{count} шт"

    def get_3_type_dish_count(self, count: int) -> str:
        """Возвращает визуализированные данные когда блюдо измеряется по массе
        в граммах
        Args:
            count: кол-во блюда
        """
        logger.info(f"Блюдо измеряется по массе")
        return f"{count} грамм"

    def get_4_type_dish_count(self, count: int) -> str:
        """Возвращает визуализированные данные когда блюдо измеряется по объему
        в миллититрах
        Args:
            count: кол-во блюда
        """
        logger.info(f"Блюдо измеряется по объему")
        return f"{count} мл"
