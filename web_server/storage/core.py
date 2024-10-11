import logging

import config
from database import storage_choicer

logger = logging.getLogger(__name__)


class StorageCommon:
    """Класс отвечающий за обобщенное взаимодействие
    с хранилищем данных"""
    client_obj = storage_choicer.choice_client_obj(storage_type=config.STORAGE_TYPE)
    auth_obj = storage_choicer.choice_auth_obj(storage_type=config.STORAGE_TYPE)


if __name__ == '__main__':
    import asyncio
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
    obj = StorageCommon()
    print(asyncio.run(obj.auth_obj.get_data_by_token(token="8ad3bc92-151f-11ef-a446-9408535897fd")))