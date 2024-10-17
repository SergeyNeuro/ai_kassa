import logging
import shutil
import os
from datetime import datetime


from fastapi import APIRouter, UploadFile, File

from config import PHOTO_DATASET_PATH



logger = logging.getLogger(f"app.{__name__}")

router = APIRouter(prefix="/dataset", tags=['dataset'])


@router.post('/upload')
async def save_dataset_image(customer_id: int, file: UploadFile = File(...)):
    """Данный роутер получает изображение.
    Обращается в сервис для расшифровки изображения
    для предсказания того, что изображено на фото
    """
    path = f"{PHOTO_DATASET_PATH}/customer_{customer_id}"

    # Проверим, существует ли папка, если нет - создадим
    os.makedirs(PHOTO_DATASET_PATH, exist_ok=True)

    # Получаем текущее время для создания уникального имени файла
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Создаем имя файла с текущей датой и временем
    file_name = f"frame_{current_time}.jpg"

    # Полный путь к сохранению файла
    file_path = os.path.join(path, file_name)

    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"success": True}