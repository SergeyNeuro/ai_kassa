import logging

import config
from storage.database import storage_choicer
from storage.database.cache import cache_choicer

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
    r_keeper_credentials = choicer.r_keeper_credentials_obj()
    r_keeper_dish = choicer.r_keeper_dish_obj()
    iiko_credentials_obj = choicer.iiko_credentials_obj()
    iiko_terminals_obj = choicer.iiko_terminals_obj()
    iiko_dishes_obj = choicer.iiko_dishes_obj()
    customers_obj = choicer.customers_obj()
    kassa_obj = choicer.kassa_obj()
    food_point = choicer.food_point_obj()
    cache = cache_choicer.get_cache_obj(key=config.CACHE_NAME)

if __name__ == '__main__':
    import asyncio
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s")
    obj = StorageCommon()
    # obj.cache.get_single_data_from_cache(key="key")
    # print(asyncio.run(obj.cache.get_single_data_from_cache(key="key")))
    # print(asyncio.run(obj.dish_obj.get_data_by_menu_and_code_name(menu_id=2, code_name="vypechka_sochnik")))
    # print(asyncio.run(obj.changing_dish_obj.get_data_by_id(node_id=1)))
    print(asyncio.run(obj.dish_obj.get_data_by_menu_and_code_names(
        menu_id=2,
        code_names=[
            "vypechka_sochnik",
            "vypechka_bulochka",
            "napitki_suhofrukty_kompot_200"
        ])
    ))
    # print(asyncio.run(obj.week_day_dish.get_dish_list_by_week_day_and_changing_id(changing_id=3, week_day=2)))