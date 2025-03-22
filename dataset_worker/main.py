import logging
import os
import asyncio
import zipfile
import shutil
from typing import Optional, List, Dict, Union
import datetime as dt
import requests

import numpy as np
from io import BytesIO
from PIL import Image

import cv2
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram import F
from aiogram.types import ContentType

from diagram_writer import DiagramWriter

COLORS = {
    0: (0, 100, 0),
    1: (139, 0, 0),
    2: (0, 0, 139),
    3: (255, 255, 0),
    4: (255, 165, 0),
    5: (128, 0, 128),
    6: (127, 255, 0),
    7: (255, 192, 203),
    8: (135, 206, 235),
    9: (230, 230, 250),
    10: (0, 128, 0),
    11: (255, 0, 0),
    12: (0, 0, 255),
    13: (160, 32, 240),
    14: (144, 238, 144),
    15: (255, 127, 80),
    16: (173, 216, 230),
    17: (221, 160, 221),
    18: (0, 160, 0),
    19: (255, 99, 71),
    20: (70, 130, 180),
    21: (186, 85, 211)
}

load_dotenv()   # load bot TOKEN

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")

"""Aiogram objects"""
bot = Bot(TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)


# Папка для временного хранения файлов
TEMP_FOLDER = 'tmp_in'

# Создаем папку, если она не существует
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)


@dp.message(lambda message: message.document and message.document.mime_type == 'application/zip')
async def handle_document(message: types.Message):
    # Проверяем, что файл является архивом
    if message.document.mime_type == 'application/zip':
        # Скачиваем архив
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        downloaded_file = await bot.download_file(file_path)

        # Сохраняем архив во временную папку
        zip_path = os.path.join(TEMP_FOLDER, 'archive.zip')
        with open(zip_path, 'wb') as new_file:
            new_file.write(downloaded_file.read())

        # Распаковываем архив
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(TEMP_FOLDER)


        await message.answer("Получил архив. Приступаю к обработке информации")

        diagram_obj = DiagramWriter()

        names = diagram_obj.get_names_dict(file_path="./tmp_in/data.yaml")

        data, file_categories = diagram_obj.get_all_frame_category(dir_path="./tmp_in/labels/train")

        diagram_obj.create_diagram(data=data)

        diagram_obj.create_txt_file(data=data, names_dict=names, file_categories=file_categories)


        await message.answer_document(FSInputFile(f"./tmp_out/histogram.png"))
        await message.answer_document(FSInputFile(f"./tmp_out/obj.txt"))
        await message.answer_document(FSInputFile(f"./tmp_out/obj.xlsx"))

        # Удаляем временную папку целиком, включая подпапки
        shutil.rmtree(TEMP_FOLDER)

        # Создаем временную папку заново (для следующих запросов)
        os.makedirs(TEMP_FOLDER)
    else:
        await message.answer("Пожалуйста, отправьте ZIP архив.")



@dp.message(F.content_type.in_([ContentType.PHOTO]))
async def handle_image(message: types.Message):
    photo = message.photo[-1]  # Берем самое большое доступное фото
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    # Скачиваем файл
    await bot.download_file(file_path, "tmp.jpg")

    menu_id = message.caption
    resized_frame = cv2.imread("./tmp.jpg")
    resized_frame = cv2.resize(resized_frame, (640, 640))

    res = send_image_to_predict(image=resized_frame, menu_id=int(menu_id))

    total_string = ""
    for index, one_dish in enumerate(res):
        paint_draw(
            image=resized_frame,
            top_corner=(int(one_dish["x1"]), int(one_dish["y1"])),
            bot_corner=(int(one_dish["x2"]), int(one_dish["y2"])),
            label=str(index + 1),
            color=COLORS[index]
        )
        total_string += f"{index + 1}) code_name: {one_dish['dish_data']['code_name']}\n"
    cv2.imwrite("./tmp.jpg", resized_frame)

    await message.answer_document(FSInputFile(f"./tmp.jpg"), caption=total_string)


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

def send_image_to_predict(image: np.ndarray, menu_id: int) -> Optional[List[Dict[str, Union[list, int]]]]:
    """Метод для отправки фотографии на удаленный сервер
    Args:
        image: изображение в формате numpy.ndarray
    return: словарь с данными об распознанных блюдах
    """
    # return TestWebCore().send_image_to_predict(image)
    try:
        # Преобразуем массив NumPy в объект PIL
        rgb_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        pil_image = Image.fromarray(rgb_frame)

        # Сохраняем изображение в байтовый поток
        img_byte_arr = BytesIO()
        pil_image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)  # Перемещаем указатель в начало потока

        logger.info(f"Отправляю файл на по адресу: https://app.neurotaw.beget.tech/api/predict")

        response = requests.post(
            url=f"https://app.neurotaw.beget.tech/api/predict/",
            headers={"AuthToken": "nyy9khmYqlQ9LfVbzpNF1RCjSa_IGvf9twxcKm_x17Y"},
            params={"menu_id": menu_id, "timestamp": int(dt.datetime.now().timestamp()), "kassa_id": 1},
            files={"file": img_byte_arr}
        ).json()

        logger.info(f"Пришел ответ от сервера: {response}")
        if response.get("success"):
            return response["data"]
    except Exception as _ex:
        logger.error(f"Ошибка при отправке фотографии на сервер -> {_ex}")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())



