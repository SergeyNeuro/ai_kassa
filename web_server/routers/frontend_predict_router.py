# web_server/routers/frontend_predict_router.py
import os
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse # импортирован и используется только для временной раздачи изображения

from config import STATIC_FILES_PATH, COOKIE_NAME
from servises.yolo_predicter import AiKassaService
from servises.dish_service import DishService
from schemas import logic_schemas
from utils import decode_token

logger = logging.getLogger("app.frontend_predict")
router = APIRouter()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# === POST: обработка фото и показ результата ===
@router.post("/predict/upload", response_class=HTMLResponse)
async def handle_upload(
    request: Request,
    file: UploadFile = File(...),
    service = Depends(AiKassaService)
):
    cookie_token = request.cookies.get(COOKIE_NAME)
    user_data = decode_token(string=cookie_token)
    if not user_data:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Пустой файл")

    uploads_dir = os.path.join(STATIC_FILES_PATH, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    safe_name = file.filename or "upload.jpg"
    save_path = os.path.join(uploads_dir, safe_name)
    with open(save_path, "wb") as f:
        f.write(data)

    try:
        result = await service.get_prediction_data_for_test(
            menu_id=user_data.get("menu_id"),
            file_data=data,
            token=cookie_token
        )
        predictions = result.get("total_list")
        image_url = result.get("image_url")
    except Exception as e:
        logger.exception("Ошибка инференса")
        return templates.TemplateResponse(
            "upload.html",
            {"request": request, "error": f"Ошибка распознавания: {e}"},
            status_code=500,
        )

    # Преобразуем результаты для таблицы
    rows = []
    for idx, item in enumerate(predictions, 1):
        dish_data = item.get("dish_data")
        if isinstance(dish_data, list) and dish_data:
            dish_data = dish_data[0]
        if not dish_data:
            continue

        row = {
            "idx": idx,
            "name_ru": dish_data.get("name_ru", dish_data.get("name", "Неизвестно")),
            "category_ru": dish_data.get("category", "—"),
            "unit": dish_data.get("unit", "шт"),
            "amount": dish_data.get("amount", 1),
            "price_rub": float(dish_data.get("price_rub", dish_data.get("price", 0.0))),
            "yolo_name": dish_data.get("code_name", ""),
        }
        rows.append(row)

    subtotal = sum(r["price_rub"] for r in rows)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "image_url": image_url,
            "rows": rows,
            "subtotal": subtotal,
        },
    )

@router.get("/predict/photo/{file_name}")
async def get_predict_photo(
        request: Request,
        file_name: str
):
    cookie_token = request.cookies.get(COOKIE_NAME)
    user_data = decode_token(string=cookie_token)
    if not user_data:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    file_path = os.path.join("/var/ai_kassa/predict", file_name)
    """Выгружаем содержимое загруженного фото которое получилось после успешного предсказания"""
    return FileResponse(
        file_path,
        media_type="image/jpeg",
        filename=file_path
    )

@router.post("/predict/confirm")
async def confirm_order(
    request: Request,
    service: DishService = Depends(DishService)
):
    """Переходим к этапу оплаты, (тестовый метод)"""
    try:
        cookie_token = request.cookies.get(COOKIE_NAME)
        user_data = decode_token(string=cookie_token)
        if not user_data:
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

        data: logic_schemas.ai_kassa_predict.TestConfirmSchem = service.cache.get_data_from_cache(
            key=cookie_token,
            data_class=logic_schemas.ai_kassa_predict.TestConfirmSchem
        )
        res = await service.confirm_pay(
            menu_id=user_data.get("menu_id"),
            kassa_id=user_data.get("kassa_id"),
            dishes_data=data.data
        )

        return {"success": res}

    except Exception as _ex:
        logger.error(f"Ошибка при подтверждении заказа -> {_ex}")
        return {"success": False}

