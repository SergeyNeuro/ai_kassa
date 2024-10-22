import logging

import config
from .database import storage_choicer

logger = logging.getLogger(__name__)


class StorageCommon:
    """Класс отвечающий за обобщенное взаимодействие
    с хранилищем данных"""
    choicer = storage_choicer.StorageTypeChoicer(storage_type=config.STORAGE_TYPE)

    auth_obj = choicer.choice_auth_obj()
    menu_obj = choicer.choice_menu_obj()
    changing_dish_obj = choicer.choice_changing_dish_obj()
    dish_obj = choicer.choice_dish_obj()
    week_day_dish = choicer.week_day_dish_obj()

if __name__ == '__main__':
    import asyncio
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
    obj = StorageCommon()
    # print(asyncio.run(obj.auth_obj.get_data_by_token(token="test")))
    # print(asyncio.run(obj.menu_obj.get_data_by_id(node_id=1)))
    # print(asyncio.run(obj.changing_dish_obj.get_data_by_id(node_id=1)))
    # print(asyncio.run(obj.dish_obj.get_data_by_menu_and_code_names(menu_id=1, code_names=["b3"])))
    print(asyncio.run(obj.week_day_dish.get_dish_list_by_week_day_and_changing_id(changing_id=3, week_day=2)))