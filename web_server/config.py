from dotenv import load_dotenv
import os

# Выгрузка секретных данных из айда .env. Данный файл должен лежать в данной директории.
load_dotenv()


STORAGE_TYPE = "cache_db"
DB_TYPE = "postgres_alchemy"
CACHE_NAME = "redis"

# глобальные переменные для работы с postgres БД
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_EX = os.getenv("REDIS_EX")

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", 120))
COOKIE_NAME = os.getenv("COOKIE_NAME", "ai_kassa_auth")

STATIC_FILES_PATH = os.getenv("STATIC_FILES_PATH")