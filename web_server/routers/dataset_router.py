import logging

from fastapi import APIRouter, UploadFile, File

from servises.yolo_predicter import YoloPredicter



logger = logging.getLogger(f"app.{__name__}")

router = APIRouter(prefix="/predict", tags=['predict'])


@router.post('/')
async def predict_image_data(file: UploadFile = File(...)):
    """Данный роутер получает изображение.
    Обращается в сервис для расшифровки изображения
    для предсказания того, что изображено на фото
    """
    contents = await file.read()

    print(type(contents))
    obj = YoloPredicter()

    res = await obj.predict(content=contents)
    return {"success": True}