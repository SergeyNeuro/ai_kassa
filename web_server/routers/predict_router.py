import asyncio
import logging
from typing import Any, Union, List
from datetime import datetime
import os
from PIL import Image
import io

from fastapi import APIRouter, UploadFile, File, Depends, Request
from fastapi.responses import JSONResponse

from servises.yolo_predicter import AiKassaService
from servises.dish_service import DishService
from servises.auth_service import get_token_by_headers, AuthObj
from schemas import logic_schemas
from config import STATIC_FILES_PATH


logger = logging.getLogger(f"app.{__name__}")

router = APIRouter(prefix="/predict", tags=['predict'])


@router.post('/')
async def predict_image_data(
        request: Request,
        menu_id: int,
        timestamp: int,
        kassa_id: int,
        token: Union[str, None] = Depends(get_token_by_headers),
        auth_obj=Depends(AuthObj),
        file: UploadFile = File(...),
        ai_obj = Depends(AiKassaService)
):
    """Данный роутер получает изображение.
    Обращается в сервис для расшифровки изображения
    для предсказания того, что изображено на фото
    Args:
        menu_id: идентификатор меню от которого приходит запрос
        timestamp: дата отправки запроса
        kassa_id: идентификатор кассы от которой приходит запрос
        token: токен доступа
        auth_obj: объект для прохождения аутентификации
        file: отправляемый файл
        ai_obj: объект с бизнес логикой
    """

    # проверяем токен на валидность
    try:
        logger.info(f"Пришел запрос от кассового аппарата №{kassa_id}. menu_id: {menu_id} на опознание фотографии")

        headers = request.headers
        possible_headers = [
            "X-Forwarded-For",
            "X-Real-IP",
            "CF-Connecting-IP",  # Cloudflare
            "True-Client-IP",  # Akamai, Cloudflare
        ]

        for header in possible_headers:
            if header in headers:
                ip = headers[header].split(",")[0].strip()
                logger.info(f"IP адрес с которго пришел запрос: {ip}. Касса: {kassa_id}, menu: {menu_id}")

        # # имитационная логика
        # await asyncio.sleep(10)
        # imit_data = [
        #     {
        #         "dish_data": [
        #             {
        #                 "id": 1,
        #                 "name": "Салат летний",
        #                 "menu_id": 1,
        #                 "code_name": "Drone",
        #                 "type": 1,
        #                 "count_type": 11,
        #                 "count": 1,
        #                 "price": 4,
        #                 "changing_dish_id": None
        #             },
        #             {
        #                 "id": 1,
        #                 "name": "Салат зимний",
        #                 "menu_id": 1,
        #                 "code_name": "fly",
        #                 "type": 1,
        #                 "count_type": 11,
        #                 "count": 1,
        #                 "price": 4,
        #                 "changing_dish_id": None
        #             },
        #             {
        #                 "id": 1,
        #                 "name": "Салат весенний",
        #                 "menu_id": 1,
        #                 "code_name": "helicopter",
        #                 "type": 1,
        #                 "count_type": 11,
        #                 "count": 1,
        #                 "price": 4,
        #                 "changing_dish_id": None
        #             },
        #         ],
        #         "x1": 350,
        #         "y1": 102,
        #         "x2": 486,
        #         "y2": 323
        #     },
        #     {
        #         "dish_data": {
        #             "id": 1,
        #             "name": "Рис с котлетой",
        #             "menu_id": 1,
        #             "code_name": "human",
        #             "type": 3,
        #             "count_type": 11,
        #             "count": 1,
        #             "price": 4,
        #             "changing_dish_id": None
        #         },
        #         "x1": 133,
        #         "y1": 85,
        #         "x2": 272,
        #         "y2": 330
        #     },
        #     {
        #         "dish_data": [
        #             {
        #                 "id": 1,
        #                 "name": "Солянка",
        #                 "menu_id": 1,
        #                 "code_name": "Phone",
        #                 "type": 2,
        #                 "count_type": 11,
        #                 "count": 1,
        #                 "price": 4,
        #                 "changing_dish_id": None
        #             },
        #             {
        #                 "id": 1,
        #                 "name": "Рассольник",
        #                 "menu_id": 1,
        #                 "code_name": "pult",
        #                 "type": 2,
        #                 "count_type": 11,
        #                 "count": 1,
        #                 "price": 4,
        #                 "changing_dish_id": None
        #             },
        #         ],
        #         "x1": 224,
        #         "y1": 385,
        #         "x2": 380,
        #         "y2": 570
        #     },
        #     {
        #         "dish_data": [
        #             {
        #                 "id": 1,
        #                 "name": "Компот яблочный",
        #                 "menu_id": 1,
        #                 "code_name": "Phone",
        #                 "type": 9,
        #                 "count_type": 4,
        #                 "count": 1,
        #                 "price": 4,
        #                 "changing_dish_id": None
        #             },
        #             {
        #                 "id": 1,
        #                 "name": "Сок яблочный",
        #                 "menu_id": 1,
        #                 "code_name": "pult",
        #                 "type": 9,
        #                 "count_type": 4,
        #                 "count": 1,
        #                 "price": 4,
        #                 "changing_dish_id": None
        #             },
        #         ],
        #         "x1": 446,
        #         "y1": 400,
        #         "x2": 525,
        #         "y2": 530
        #     },
        # ]
        # return JSONResponse(status_code=200, content={"success": True, "data": imit_data})

        auth_data =  await auth_obj.check_authenticate(token=token, api="predict")
        if not auth_data:
            return JSONResponse(status_code=403, content={"success": False, "info": "authentication error"})

        # прогоняем дальнейшую логику
        await save_image(customer_id=auth_data.customer_id, menu_id=menu_id, file=file)

        file_data = await file.read()

        predict_data = await ai_obj.get_prediction_data(
            customer_id=auth_data.customer_id,
            menu_id=menu_id,
            file_data=file_data
        )
        if predict_data:
            return JSONResponse(status_code=200, content={"success": True, "data": predict_data})
        else:
            return JSONResponse(status_code=400, content={"success": False, "info": "indefinite error"})

    except Exception as _ex:
        logger.error(f"Ошибка распознавании фотографии: {_ex}")
        return JSONResponse(status_code=400, content={"success": False, "info": "indefinite error"})


async def save_image(
        customer_id: int,
        menu_id: int,
        file: UploadFile
):
    date_folder = str(datetime.now().strftime("%d.%m.%Y").replace("20", ""))
    path = f"{STATIC_FILES_PATH}/customer_{customer_id}/menu_{menu_id}/{date_folder}"
    os.makedirs(path, exist_ok=True)
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"frame_{current_time}.jpg"
    file_path = os.path.join(path, file_name)
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data)).convert('RGB')

    # Сохраняем изображение в нужном формате
    image.save(file_path, format='JPEG')

    return {"success": True}


@router.get("/")
async def check_work(
        kassa_id: int,
        token: Union[str, None] = Depends(get_token_by_headers),
        auth_obj=Depends(AuthObj),
):
    """Данный роут проверяет работоспособность
    веб сервера. Вызывается для проверки связи между
    веб сервером и кассой
    Args:
        kassa_id: идентификатор кассы
        token: токен доступа
        auth_obj: объект для проверки аутетификации
    """
    # проверяем токен на валидность
    try:
        auth_data = await auth_obj.check_authenticate(token=token, api="check_work")
        if not auth_data:
            return JSONResponse(status_code=403, content={"success": False, "info": "authentication error"})

        logger.info(f"Пришел запрос на проверку работоспособности для кассового аппарата: {kassa_id}")
        return JSONResponse(content={"success": True})

    except Exception as _ex:
        logger.error(f"Ошибка прочекивания связи: {_ex}")
        return JSONResponse(status_code=400, content={"success": False, "info": "indefinite error"})


@router.post("/confirm")
async def confirm_pay(
        kassa_id: int,
        menu_id: int,
        data: List[logic_schemas.ai_kassa_predict.ConfirmSchem],
        token: Union[str, None] = Depends(get_token_by_headers),
        auth_obj=Depends(AuthObj),
        dish_service: DishService = Depends(DishService)
):
    """Метод подтверждения покупки через смарт кассу
    Args:
        kassa_id: идентификатор кассы на которой была сделана покупка
        menu_id: идентификатор меню, из которого была совершена покупка
        data: данные блюд которые были куплены
        token: токен дотупа
        auth_obj: объект проверки аутентификации
        dish_service: объект для работы с данными блюж
    """
    try:
        auth_data = await auth_obj.check_authenticate(token=token, api="confirm")
        if not auth_data:
            return JSONResponse(content={"success": True})

        # вызываем метод объекта для подтверждения покупки
        res = await dish_service.confirm_pay(menu_id=menu_id, kassa_id=kassa_id, dishes_data=data)
        if res:
            return JSONResponse(content={"success": True})
        else:
            return JSONResponse(content={"success": False})

    except Exception as _ex:
        logger.error(f"Ошибка подтверждения покупки: {_ex}")
        return JSONResponse(status_code=400, content={"success": False, "info": "indefinite error"})


@router.get("/barcode")
async def get_barcode_data(
        menu_id: int,
        barcode: str,
        token: Union[str, None] = Depends(get_token_by_headers),
        auth_obj=Depends(AuthObj),
        dish_service: DishService = Depends(DishService)
):
    """Метод извлечения данный блюда по штрихкоду
    Args:
        menu_id: идентификатор меню
        barcode: расшифрованный штрихкод
        token: токен доступа
        auth_obj: объект для проверки аутентификации
        dish_service: логический объект
    """
    try:
        auth_data = await auth_obj.check_authenticate(token=token, api="barcode")
        if not auth_data:
            return JSONResponse(content={"success": False})

        # вызываем метод объекта для подтверждения покупки
        res = await dish_service.get_dish_by_barcode(menu_id=menu_id, barcode=barcode)
        if res:
            return JSONResponse(content={"success": True, "data": {"dish_data": res.model_dump()}})
        else:
            return JSONResponse(content={"success": False})

    except Exception as _ex:
        logger.error(f"Ошибка при поиске по баркоду: {_ex}")
        return JSONResponse(status_code=400, content={"success": False, "info": "indefinite error"})