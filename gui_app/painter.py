"""Модуль с логикой отметки на изображениях
объектов и добавление подписей к ним
"""
import logging

import cv2
import numpy as np


class Painter:
    def __init__(self, image: np.ndarray, top_corner: tuple, bot_corner: tuple, label: str, color: tuple):
        """Изменяем объект изображения
        Args:
            image: изображение в формате массива numpy
            top_corner: координаты верхнего левого угла (x, y)
            bot_corner: координаты нижнего правого угла (x, y)
            label: подпись к объекту
            color: цвет прямоугольника и подписи к нему
        """
        self.image = self.paint_draw(
            image=image,
            top_corner=top_corner,
            bot_corner=bot_corner,
            label=label, color=color
        )

    @staticmethod
    def paint_draw(image: np.ndarray, top_corner: tuple, bot_corner: tuple, label: str, color: tuple):
        """Изменяем объект изображения
        Args:
            image: изображение в формате массива numpy
            top_corner: координаты верхнего левого угла (x, y)
            bot_corner: координаты нижнего правого угла (x, y)
            label: подпись к объекту
            color: цвет прямоугольника и подписи к нему
        """

        # Рисуем прямоугольник
        cv2.rectangle(image, top_corner, bot_corner, color=color, thickness=2)  # Зеленый цвет

        # Добавляем текст с названием объекта
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.8  # высота цифры
        font_color = color  # Белый цвет
        font_thickness = 2  # ширина цифры

        # Определяем позицию текста
        text_size = cv2.getTextSize(label, font, font_scale, font_thickness)[0]
        text_x = (bot_corner[0] + top_corner[0] - 15) // 2
        text_y = top_corner[1] - 10  # Положение текста немного выше квадрата

        # Рисуем текст
        cv2.putText(image, label, (text_x, text_y), font, font_scale, font_color, font_thickness)

        return image


if __name__ == '__main__':

    img = cv2.imread("/home/udalov/Изображения/Снимки экрана/Снимок экрана от 2024-10-23 13-23-48.png")

    img = cv2.resize(img, (640, 640))
    obj = Painter(
        image=img,
        top_corner=(282, 304),
        bot_corner=(319, 377),
        label="1",
        color=(0, 255, 0)
    )

    cv2.imshow("Image with Rectangle", obj.image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
