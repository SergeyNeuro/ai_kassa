import logging
import os
import asyncio
import zipfile
import shutil

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile

from diagram_writer import DiagramWriter

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

        # Удаляем временную папку целиком, включая подпапки
        shutil.rmtree(TEMP_FOLDER)

        # Создаем временную папку заново (для следующих запросов)
        os.makedirs(TEMP_FOLDER)
    else:
        await message.answer("Пожалуйста, отправьте ZIP архив.")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())



