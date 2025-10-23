# web_server/routers/frontend_predict_router.py
import os
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
# from fastapi.responses import FileResponse # импортирован и используется только для временной раздачи изображения

from config import STATIC_FILES_PATH
from servises.yolo_predicter import AiKassaService  

logger = logging.getLogger("app.frontend_predict")
router = APIRouter()

COOKIE_NAME = os.getenv("COOKIE_NAME", "ai_kassa_auth")

def _is_authenticated(request: Request) -> bool:
    return bool(request.cookies.get(COOKIE_NAME))


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# @router.get("/predict/image/{fname}")                      # отдаёт файл из /var/ai_kassa/predict
# async def serve_predict_image(fname: str):
#     # отдаём файл из /var/ai_kassa/predict
#     path = os.path.join(STATIC_FILES_PATH, "predict", fname)
#     if not os.path.isfile(path):
#         raise HTTPException(status_code=404, detail="Изображение не найдено")
#     return FileResponse(path, media_type="image/jpeg")

# === POST: обработка фото и показ результата ===
@router.post("/predict/upload", response_class=HTMLResponse)
async def handle_upload(
    request: Request,
    file: UploadFile = File(...),
    customer_id: int = Form(1),
    menu_id: int = Form(1),
):
    if not _is_authenticated(request):
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

    service = AiKassaService()
    try:
        result = await service.get_prediction_data(
            customer_id=customer_id,
            menu_id=menu_id,
            file_data=data,
        )

        # поддержка нового формата
        # if isinstance(result, dict):
        #     predictions = result.get("total_list", [])
        #     img_field = result.get("image_url")
        #     fname = os.path.basename(img_field) if img_field else os.path.basename(safe_name)
        # else:
        #     predictions = result
        #     # fallback: покажем загруженный оригинал, если нужно
        #     fname = os.path.basename(safe_name)

        # image_url = f"/predict/image/{fname}"
        if isinstance(result, dict):
            predictions = result.get("total_list", [])
            image_url = result.get("image_url", f"/static/uploads/{safe_name}")
        else:
            predictions = result
            image_url = f"/static/uploads/{safe_name}"
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
            "category_ru": dish_data.get("category_ru", "—"),
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
