
from storage.base_interface import database

from . import cache_db


class StorageTypeChoicer:
    """
    Класс содержит логику выбора объектов
    для взаимодействия с хранилищем данных
    исходя из глобальной переменной DB_TYPE
    """
    def __init__(self, storage_type: str):
        self.storage_type = storage_type

    def choice_auth_obj(self) -> database.BaseAuth:
        """
        Метод выбирает объект для взаимодействия
        с данными аутентификации (исходя из глобальных настроек)
        """
        data_dict = {
            "cache_db": cache_db.AuthDbCache
        }
        return data_dict[self.storage_type]()

    def choice_menu_obj(self) -> database.BaseMenu:
        """
        Метод выбирает объект для взаимодействия
        с данными меню (исходя из глобальных настроек)
        """
        data_dict = {
            "cache_db": cache_db.MenuDbCache
        }
        return data_dict[self.storage_type]()

    def choice_changing_dish_obj(self) -> database.BaseChangingDish:
        """
        Метод выбирает объект для взаимодействия
        с данными сомневающихся позиций (исходя из глобальных настроек)
        """
        data_dict = {
            "cache_db": cache_db.ChangingDishDbCache
        }
        return data_dict[self.storage_type]()

    def choice_dish_obj(self) -> database.BaseDish:
        """
        Метод выбирает объект для взаимодействия
        с данными блюд (исходя из глобальных настроек)
        """
        data_dict = {
            "cache_db": cache_db.DishDbCache
        }
        return data_dict[self.storage_type]()

    def week_day_dish_obj(self) -> database.BaseWeekDayDish:
        """
        Метод выбирает объект для взаимодействия
        с данными блюд зависимых от дня недели
        """
        data_dict = {
            "cache_db": cache_db.WeekDayDishDbCache
        }
        return data_dict[self.storage_type]()

    def r_keeper_credentials_obj(self) -> database.BaseRKeeperCredentials:
        """
        Метод выбирает объект для взаимодействия
        с данными авторизации в системе r-keeper
        """
        data_dict = {
            "cache_db": cache_db.RKeeperCredentialsDbCache
        }
        return data_dict[self.storage_type]()

    def r_keeper_dish_obj(self) -> database.BaseRKeeperDish:
        """
        Метод выбирает объект для взаимодействия
        с данными блюд из системы r-keeper
        """
        data_dict = {
            "cache_db": cache_db.RKeeperDishDbCache
        }
        return data_dict[self.storage_type]()

    def iiko_credentials_obj(self) -> database.BaseIikoCredentials:
        """
        IIKO credentials
        """
        data_dict = {
            "cache_db": cache_db.IikoCredentialsDbCache
        }
        return data_dict[self.storage_type]()

    def iiko_terminals_obj(self) -> database.BaseIikoTerminals:
        """
        IIKO terminal
        """
        data_dict = {
            "cache_db": cache_db.IikoTerminalsDbCache
        }
        return data_dict[self.storage_type]()

    def iiko_dishes_obj(self) -> database.BaseIikoDishes:
        """
        IIKO dishes
        """
        data_dict = {
            "cache_db": cache_db.IikoDishesDbCache
        }
        return data_dict[self.storage_type]()

    def customers_obj(self) -> database.BaseCustomer:
        """
        customers
        """
        data_dict = {
            "cache_db": cache_db.CustomersDbCache
        }
        return data_dict[self.storage_type]()

    def kassa_obj(self) -> database.BaseKassa:
        """
        customers
        """
        data_dict = {
            "cache_db": cache_db.KassaDbCache
        }
        return data_dict[self.storage_type]()

    def food_point_obj(self) -> database.BaseFoodPoint:
        """
        customers
        """
        data_dict = {
            "cache_db": cache_db.FoodPointDbCache
        }
        return data_dict[self.storage_type]()