import logging
from sys import prefix

from fastapi import FastAPI

# импорируем роутеры
from routers.predict_router import router as predict_router
from routers.dataset_router import router as dataset_router
from routers.iiko import router as iiko_roter


# выставляем логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
logger = logging.getLogger("app")


API_PREFIX = "/api"


app = FastAPI(title='AI Kassa')


app.include_router(predict_router, prefix=API_PREFIX)
app.include_router(dataset_router, prefix=API_PREFIX)
app.include_router(iiko_roter, prefix=API_PREFIX)