from dotenv import load_dotenv
import os

# Выгрузка секретных данных из айда .env. Данный файл должен лежать в данной директории.
load_dotenv()


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")