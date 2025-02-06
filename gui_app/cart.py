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
    QLineEdit, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont
import numpy
import cv2

from config import DISTH_TYPE, COUNT_TYPE, COLORS, FONT
from painter import Painter
from config import HEIGHT, WIDTH
from schemas import DishSchem, OperationSchem
from pay.base_pay_manager import IngenicoPay
from pay.base_check_manager import Atol

logger = logging.getLogger(f"app.{__name__}")


class CartKassaTerminalThread(QThread):
    finished = pyqtSignal(bool, str)  # Сигнал для передачи результата оплаты

    def __init__(self, pay_manager: IngenicoPay, check_manager: Atol, dishes_data: list):
        super().__init__()
        self.pay_manager = pay_manager
        self.check_manager = check_manager
        self.dishes_data = dishes_data


    def run(self):
        """Проводим логику оплаты заказа"""
        logger.info("Обрабатываю ивент на оплату")
        total_price = 0
        for one_dish in self.dishes_data:
            if type(one_dish["dish_data"]) == list:
                logger.error(f"Заполнена информация не по всем блюдам. Спорная ситуаци: {one_dish['dish_data']}")
                # return OperationSchem(success=False, info="Заполнен информация не по всем блюдам")
                self.finished.emit(False, "Заполнен информация не по всем блюдам")
                return
            else:
                total_price += one_dish["dish_data"]["price"]
        else:  # выполняется если цикл корректно завершился
            logger.info(f"Сумма оплаты заказа: {total_price}")
            # отправляем информацию на платежный терминал
            logger.info(f"Отправляю информацию на платежный терминал на сумму {total_price} рублей")
            pay = self.pay_manager.pay(value=int(total_price * 100))

            if pay.success:
                # создаем чек
                self.check_manager.execute(
                    self.check_manager.create_check,
                    ([DishSchem.model_validate(item["dish_data"]) for item in self.dishes_data],)
                )
                # return OperationSchem(success=True, info="Оплата прошла успешно")
                self.finished.emit(True, "Оплата прошла проведена")
            else:
                # return OperationSchem(success=False, info=pay.info)
                self.finished.emit(False, pay.info)
            
        
class CartWindow(QWidget):
    """Окно корзины с изображением и кнопками"""

    def __init__(self, image: numpy.ndarray, dishes_data: list, pay_manager: IngenicoPay, check_manager: Atol):
        super().__init__()
        self.pay_manager = pay_manager
        self.check_manager = check_manager

        # отправляем изображение на веб сервер, для предсказания какие блюда на фото
        self.dishes_data = dishes_data

        if not self.dishes_data:
            QMessageBox.warning(None, "Ошибка!!!", "Не удалось распознать блюда")

        else:
            self.image = image

            # настраиваем главное окно
            self.setWindowTitle("Корзина")
            self.setGeometry(100, 100, WIDTH, HEIGHT)  # Размеры окна
            self.main_layout = QHBoxLayout()

            # Добавляем разделительную полосу между левым и правым блоком
            self.main_layout.setSpacing(10)

            # Левый виджет для изображения
            self.create_left_widget()

            # правый виджет для информации о блюдах в котором будет происходить все взаимодействие
            self.create_right_widget()

            # инициализируем главный слой
            self.setLayout(self.main_layout)

    def enter_full_screen(self):
        """Вход в полноэкранный режим"""
        self.showFullScreen()

    def start_pay_event(self):
        """Запускаем ивент на работу с устройствами оплаты в отдельном потоке"""
        # блокируем все кнопки, чтобы во время оплаты пользователь не нажал лишнего
        self.toggle_buttons()
        self.thread = CartKassaTerminalThread(
            pay_manager=self.pay_manager, 
            check_manager=self.check_manager,
            dishes_data=self.dishes_data
            )
        self.thread.finished.connect(self.on_pay_finished)
        self.thread.start()

    def on_pay_finished(self, success: bool, info: str):
        """callback обработка ивента оплаты
        Args:
            
        """
        # разблокируем все кнопки, чтобы во время оплаты пользователь не нажал лишнего
        self.toggle_buttons()

        if success:
            QMessageBox.information(None, "Оплата", "Оплата прошла успешно")
            self.close()
        else:
            QMessageBox.critical(None, "Ошибка!!!", info)

    def toggle_buttons(self):
        """Блокировка или разблокировка всех кнопок на странице"""
        # Находим все кнопки на странице
        buttons = self.findChildren(QPushButton)
        # Переключаем состояние каждой кнопки
        for button in buttons:
            button.setEnabled(not button.isEnabled())

    def create_left_widget(self):
        """Настройка левого виджета окна корзины. В левой части находится изображение
        с распознанными блюдами
        """
        # Левый виджет для изображения
        self.image_label = QLabel()
        self.set_image(self.image)
        self.main_layout.addWidget(self.image_label)
        self.setStyleSheet("background-color: #ffffff;")

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
            # print(one_dish)
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
        self.image_label.setPixmap(
            QPixmap.fromImage(q_image).scaled(int(WIDTH * 0.4), HEIGHT, Qt.AspectRatioMode.KeepAspectRatio))

    def fill_tail_dishes_layout(self, layout: QGridLayout, count_func: bool = False):
        """Создаем верхнюю шапку таблицы
        Args:
            layout: слой на который необходим нанести виджеты
            count_func: случай когда создается шапка для виджета изменения кол-ва блюда
        """
        font = QFont("Arial", FONT)  # Установить размер шрифта
        self.add_label(layout=layout, text="№", font=font, row=0, column=0, text_color="black", center=True)
        self.add_label(layout=layout, text="Название", font=font, row=0, column=1, text_color="black")
        self.add_label(layout=layout, text="Тип блюда", font=font, row=0, column=2, text_color="black")
        self.add_label(layout=layout, text="Кол-во", font=font, row=0, column=3, text_color="black")
        if count_func:
            self.add_label(layout=layout, text="Ед. изм.", font=font, row=0, column=4, text_color="black")
            self.add_label(layout=layout, text="Цена, руб", font=font, row=0, column=5, text_color="black")
        else:
            self.add_label(layout=layout, text="Цена, руб", font=font, row=0, column=4, text_color="black")

        layout.setColumnMinimumWidth(0, 10)  # Установить минимальную ширину 1-го столбца на 100 пикселей

    def add_label(
            self,
            layout: QGridLayout,
            text: str,
            row: int,
            column: int,
            text_color: str,
            font: QFont = QFont("Arial", FONT),
            center: bool = False
    ):
        """Добавляет QLabel с заданными параметрами в layout
        Args:
            layout: слой на который необходимо вставить Label
            text: текст который должен быть написан
            font: шрифт которым должен быть написан текст
            row: номер ряда
            column: номер колонки
            text_color: цвет текста
            center: флаг который говорит нужно ли ставить виджет по центру
        """
        label = QLabel(text)
        label.setFont(font)
        label.setStyleSheet(
            f"color: {text_color}; border: 1px solid gray; padding: 5px;")  # Применяем одинаковые настройки
        if center:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # центрируем текст
        label.setWordWrap(True)
        label.setFixedHeight(40)
        layout.addWidget(label, row, column)
        return label

    def create_right_widget(self, base_layout: QGridLayout = None):
        """Настройка правого виджета корзины, на котором будут находится
        Args:
            layout: слой на который необходимо вставлять виджеты
            base_layout: слой, на котором будет отображаться логическая информация
        """
        logger.info(f"Наполнения правого слоя")
        total_price = 0  # переменная для хранения цены всего, что находится на подносе

        if not base_layout:
            logger.info(f"Правый слой не создан. Создаю его")
            base_layout = QGridLayout()
            # Устанавливаем расстояние между виджетами
            base_layout.setHorizontalSpacing(0)  # Устанавливаем горизонтальное расстояние на 0
            base_layout.setVerticalSpacing(0)  # Устанавливаем вертикальное расстояние на 0
            # Устанавливаем отступы для содержимого
            base_layout.setContentsMargins(0, 0, 0, 0)  # Устанавливаем отступы (левый, верхний, правый, нижний) на 0
            right_widget = QWidget()
            right_widget.setLayout(base_layout)
            right_widget.setStyleSheet("background-color: #ffffff;")
            # Добавляем текст
            self.fill_tail_dishes_layout(layout=base_layout)

            self.main_layout.addWidget(right_widget)

        else:
            logger.info(f"Правый слой создан. Очищаю его")
            # Устанавливаем расстояние между виджетами
            base_layout.setHorizontalSpacing(0)  # Устанавливаем горизонтальное расстояние на 0
            base_layout.setVerticalSpacing(0)  # Устанавливаем вертикальное расстояние на 0

            # Устанавливаем отступы для содержимого
            base_layout.setContentsMargins(0, 0, 0, 0)  # Устанавливаем отступы (левый, верхний, правый, нижний) на 0

            self.clear_layout(layout=base_layout)
        self.fill_tail_dishes_layout(layout=base_layout)

        for index, dish_data in enumerate(self.dishes_data):
            dish_price = self.add_one_dish_data(layout=base_layout, data=dish_data["dish_data"], index=index + 1)
            if dish_price:
                total_price += dish_price

        # показываем итоговую стоимость всего что есть на подносе
        if total_price > 0:
            self.add_label(
                layout=base_layout, text="Итого:", row=index + 2, column=3, text_color="black", center=True
            )
            self.add_label(
                layout=base_layout, text=str(total_price), row=index + 2, column=4, text_color="black"
            )

        # Добавляем кнопку Назад
        back_btn = QPushButton("\U000021A9 Назад", self)
        back_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e4eafe;
                        color: #000;
                        border: 1px solid gray;
                        padding: 10px 20px;
                        font-size: 12x;
                        border-radius: 5px;
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
                        border: 1px solid gray;
                        padding: 10px 20px;
                        font-size: 12px;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #1a237e;
                    }
                    QPushButton:pressed {
                        background-color: #0d47a1;
                    }
                """)
        # pay_btn.clicked.connect(lambda: self.pay_cart())
        pay_btn.clicked.connect(self.start_pay_event)
        base_layout.addWidget(pay_btn, index + 3, 5)
        for i in range(base_layout.rowCount()):
            base_layout.itemAt(i).widget().setSizePolicy(QSizePolicy.Policy.Expanding,
                                                         QSizePolicy.Policy.Fixed)  # Устанавливаем фиксированную высоту
            # Устанавливаем выравнивание для всего layout
        base_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Выравнивание всех элементов по верху

    def add_one_dish_data(self, layout: QGridLayout, data: Union[dict, list], index: int) -> Union[int, None]:
        """Добаление на слой данных по одному блюду + реализуется логика спорных позиций
        когда на выбор блюд несколько
        Args:
            layout: слой на который нужно добавить данные о блюде
            data: данные которые нужно занести
        : return
            Стоимость блюда, если она выбрана
        """
        font = QFont("Arial", FONT)  # Установить размер шрифта

        # номер позиции
        self.add_label(layout=layout, text=str(index), font=font, row=index, column=0, text_color="black", center=True)
        if type(data) == dict:
            logger.info(f"Добавляю информацию о блюде: {data}")
            # наименование позиции
            self.add_label(layout=layout, text=data["name"], font=font, row=index, column=1, text_color="black")
            # тип позиции
            self.add_label(layout=layout, text=DISTH_TYPE[data["type"]], font=font, row=index, column=2,
                           text_color="black")
            # количественный тип позиции
            self.add_label(
                layout=layout,
                text=self.add_dish_count_by_type(count_type=data["count_type"], count=data["count"]),
                font=font,
                row=index,
                column=3,
                text_color="black",
            )
            # цена позиции
            self.add_label(layout=layout, text=str(data["price"]), font=font, row=index, column=4, text_color="black")

            if data["count_type"] > 10:
                btn = QPushButton("Изменить кол-во", self)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e4eafe;
                        color: #000;
                        border: 1px solid gray;
                        padding: 10px 20px;
                        font-size: 12px;
                        border-radius: 5px;
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
                self.add_label(
                    layout=layout, text="Спорная позиция", font=font, row=index, column=1, text_color="black"
                )
                self.add_label(
                    layout=layout, text=DISTH_TYPE[data[0]["type"]], font=font, row=index, column=2, text_color="black"
                )
                btn = QPushButton("Выбрать блюдо", self)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e4eafe;
                        color: #000;
                        border: 1px solid gray;
                        padding: 10px 20px;
                        font-size: 12px;
                        border-radius: 5px;
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
        back_btn = QPushButton("\U000021A9 Назад", self)
        back_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e4eafe;
                        color: #000;
                        border: 1px solid gray;
                        padding: 10px 20px;
                        font-size: 12px;
                        border-radius: 5px;
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
        font = QFont("Arial", FONT)  # Установить размер шрифта
        self.add_label(layout=layout, text=str(count), font=font, row=count, column=0, text_color="black", center=True)
        self.add_label(layout=layout, text=data["name"], font=font, row=count, column=1, text_color="black")
        self.add_label(layout=layout, text=DISTH_TYPE[data["type"]], font=font, row=count, column=2, text_color="black")
        self.add_label(
            layout=layout,
            text=self.add_dish_count_by_type(count_type=data["count_type"], count=count),
            font=font,
            row=count,
            column=3,
            text_color="black"
        )
        self.add_label(layout=layout, text=str(data["price"]), font=font, row=count, column=4, text_color="black")

        btn = QPushButton("Выбрать блюдо", self)
        btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e4eafe;
                        color: #000;
                        border: 1px solid gray;
                        padding: 10px 20px;
                        font-size: 12px;
                        border-radius: 5px;
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
        self.fill_tail_dishes_layout(layout=layout, count_func=True)

        # добавляем виджеты с данными о продукте
        font = QFont("Arial", FONT)  # Установить размер шрифта
        self.add_label(
            layout=layout, text=str(index + 1), font=font, row=index + 1, column=0, text_color="black", center=True
        )  # счетчик

        self.add_label(layout=layout, text=data["name"], font=font, row=index + 1, column=1,
                       text_color="black")  # наименование блюда
        self.add_label(
            layout=layout, text=DISTH_TYPE[data["type"]], font=font, row=index + 1, column=2, text_color="black"
        )  # тип блюда

        # вставляем поле, в котором нужно вводить кол-во блюда
        self.dish_count_edit = QLineEdit(parent=self)
        self.dish_count_edit.setFont(font)
        self.dish_count_edit.setStyleSheet("color: black; background-color: lightyellow;")
        self.dish_count_edit.setPlaceholderText("Введите количество")
        self.dish_count_edit.setText(str(data["count"]))
        layout.addWidget(self.dish_count_edit, index + 1, 3)

        self.add_label(
            layout=layout, text=COUNT_TYPE[data["count_type"]], font=font, row=index + 1, column=4, text_color="black"
        )  # единица измерения блюда
        self.price_label = self.add_label(
            layout=layout, text=str(data["price"]), font=font, row=index + 1, column=5, text_color="black"
        )  # цена блюда

        # добавляем новую переменную, которая указываем минимальное значение кол-ва блюда
        if "min_count" not in data:
            data["min_count"] = data["count"]

        # добавляем кнопку для изменения кол-ва блюда
        change_btn = QPushButton("Изменить", self)
        change_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e4eafe;
                        color: #000;
                        border: 1px solid gray;
                        padding: 10px 20px;
                        font-size: 12px;
                        border-radius: 5px;
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
        back_btn = QPushButton("\U000021A9 Назад", self)
        back_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e4eafe;
                color: #000;
                border: 1px solid gray;
                padding: 10px 20px;
                font-size: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1a237e;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            """
        )
        back_btn.clicked.connect(lambda: self.back(layout=layout))
        layout.addWidget(back_btn, index + 2, 0)

        # добавляем кнопку Больше
        up_btn = QPushButton("\U000025B2", self)
        up_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e4eafe;
                color: #000;
                border: 1px solid gray;
                padding: 10px 20px;
                font-size: 12x;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1a237e;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            """
        )
        up_btn.clicked.connect(lambda: self.up_dish_count(index=index))
        layout.addWidget(up_btn, index + 2, 3)

        # добавляем кнопку Меньше
        down_btn = QPushButton("\U000025BC", self)
        down_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e4eafe;
                color: #000;
                border: 1px solid gray;
                padding: 10px 20px;
                font-size: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1a237e;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            """
        )
        down_btn.clicked.connect(lambda: self.down_dish_count(index=index))
        layout.addWidget(down_btn, index + 3, 3)

    def change_dish_count(self, index: int, layout: QGridLayout):
        """Изменяем значение кол-ва блюда и производим
        пересчет его стоимости
        """
        data = self.dishes_data[index]["dish_data"]
        new_dish_text = self.dish_count_edit.text()
        try:
            new_dish_count = int(new_dish_text)
            if new_dish_count < data["min_count"]:
                raise ValueError  # вызываем ошибку, чтобы указать что было введено не корректное значение
            new_price = (new_dish_count * data["price"]) // data["count"]
            data["price"] = new_price
            data["count"] = new_dish_count
            self.create_right_widget(base_layout=layout)
        except Exception as _ex:
            QMessageBox.warning(None, "Ошибка!!!", "Введено слишком маленькое или не корректное значение")

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

    def up_dish_count(self, index: int):
        """Увеличение кол-ва блюда
        Args:
            step: шаг на сколько за раз увеличивается блюдо
            index: индекс элемента среди списка блюд
        """
        now_value = int(self.dish_count_edit.text())
        data = self.dishes_data[index]["dish_data"]  # извлекаем информацию о блюде
        new_count = now_value + int(data["min_count"])
        self.dish_count_edit.setText(str(new_count))
        new_price = (new_count * data["price"]) // data["count"]
        data["count"] = new_count
        data["price"] = new_price
        self.price_label.setText(str(new_price))

    def down_dish_count(self, index: int):
        """Уменьшение кол-ва блюда
        Args:
            step: шаг на сколько за раз увеличивается блюдо
            index: индекс элемента среди списка блюд
        """
        now_value = int(self.dish_count_edit.text())
        data = self.dishes_data[index]["dish_data"]  # извлекаем информацию о блюде
        new_count = now_value - int(data["min_count"])
        if new_count < 0 or new_count < int(data["min_count"]):
            pass
        else:
            self.dish_count_edit.setText(str(new_count))
            new_price = (new_count * data["price"]) // data["count"]
            data["count"] = new_count
            data["price"] = new_price
            self.price_label.setText(str(new_price))


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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    object = CartWindow(numpy.random.rand(400, 400, 3), [{"dish_data": {"name": "Пицца", "type": 1, "count": 2, "price": 500}}, {"dish_data": {"name": "Салат", "type": 2, "count": 1, "price": 200}}])
    object.show()
    sys.exit(app.exec())
