import logging
from typing import Any, Union

from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse

from servises.yolo_predicter import AiKassaService
from servises.auth_service import get_token_by_headers, AuthObj



logger = logging.getLogger(f"app.{__name__}")

router = APIRouter(prefix="/predict", tags=['predict'])


@router.post('/')
async def predict_image_data(
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
    """

    # проверяем токен на валидность
    try:
        auth_data =  await auth_obj.check_authenticate(token=token, api="predict")
        if not auth_data:
            return JSONResponse(status_code=403, content={"success": False, "info": "authentication error"})

        # прогоняем дальнейшую логику

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