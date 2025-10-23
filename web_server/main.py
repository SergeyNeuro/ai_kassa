import os
import logging
from sys import prefix

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# импорируем роутеры
from routers.predict_router import router as predict_router
from routers.dataset_router import router as dataset_router
from routers.iiko import router as iiko_roter
from routers.frontend_router import router as frontend_router
from routers.auth_router import router as auth_router
from routers.frontend_predict_router import router as frontend_predict_router


# выставляем логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
logger = logging.getLogger("app")


API_PREFIX = "/api"


app = FastAPI(title='AI Kassa')


# Пути к статике и шаблонам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Инициализируем шаблонизатор
templates = Jinja2Templates(directory=TEMPLATES_DIR)


app.include_router(predict_router, prefix=API_PREFIX)
app.include_router(dataset_router, prefix=API_PREFIX)
app.include_router(iiko_roter, prefix=API_PREFIX)
app.include_router(auth_router)
app.include_router(frontend_router)
app.include_router(frontend_predict_router)