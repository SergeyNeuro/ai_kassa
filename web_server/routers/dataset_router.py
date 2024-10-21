import logging
import shutil
import os
from datetime import datetime
from typing import Union


from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse

from config import STATIC_FILES_PATH
from schemas import logic_schemas
from servises.auth_service import get_token_by_headers, AuthObj
from servises.dish_service import DishService



logger = logging.getLogger(f"app.{__name__}")

router = APIRouter(prefix="/dataset", tags=['dataset'])


@router.post('/upload')
async def save_dataset_image(
        menu_id: int,
        file: UploadFile = File(...),
        token: Union[str, None] = Depends(get_token_by_headers),
        auth_obj=Depends(AuthObj),
):
    """Данный роутер получает изображение.
    Обращается в сервис для расшифровки изображения
    для предсказания того, что изображено на фото
    """
    auth_data = await auth_obj.check_authenticate(token=token, api="add_dish")
    if not auth_data:
        return JSONResponse(status_code=403, content={"success": False, "info": "authentication error"})

    date_folder = str(datetime.now().strftime("%d.%m.%Y").replace("20", ""))
    path = f"{STATIC_FILES_PATH}/customer_{auth_data.customer_id}/menu_{menu_id}/{date_folder}"

    # Проверим, существует ли папка, если нет - создадим
    os.makedirs(path, exist_ok=True)

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


@router.post("/dish")
async def add_new_dish(
        in_data: logic_schemas.add_dish.DishSchem,
        token: Union[str, None] = Depends(get_token_by_headers),
        auth_obj=Depends(AuthObj),
        obj = Depends(DishService)
):
    """Добавляем новую блюдо в БД"""
    try:
        auth_data =  await auth_obj.check_authenticate(token=token, api="add_dish")
        if not auth_data:
            return JSONResponse(status_code=403, content={"success": False, "info": "authentication error"})
        if auth_data.role != 0:
            return JSONResponse(status_code=403, content={"success": False, "info": "authentication error"})
        data = await obj.add_new_dish(dish_data=in_data)
        if data:
            return JSONResponse(status_code=200, content={"success": True})
        else:
            return JSONResponse(status_code=400, content={"success": False})

    except Exception as _ex:
        logger.error(f"Ошибка при добавлении нового блюда: {_ex}")
        return JSONResponse(status_code=400, content={"success": False, "info": "indefinite error"})