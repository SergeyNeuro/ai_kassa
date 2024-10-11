import logging

from fastapi import FastAPI

# импорируем роутеры
from routers.predict_router import router as predict_router


# выставляем логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
logger = logging.getLogger("app")


API_PREFIX = "/api"


app = FastAPI(title='AI Kassa')


app.include_router(predict_router, prefix=API_PREFIX)