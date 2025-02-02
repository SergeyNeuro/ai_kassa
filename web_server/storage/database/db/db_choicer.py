"""storage/database/db/db_choicer
В данном модуле происходит выбор базы данных
"""

from storage.base_interface import database

from . import postgres_alchemy

class DbChoicer:
    """
    Класс содержит логику выбора объекта взаимодействия с БД
    (например postgresql)
    """
    def __init__(self, db_name: str):
        self.db_name = db_name

    def choice_auth_obj(self) -> database.BaseAuth:
        """
        Метод выбирает объект для взаимодействия с данными аутентификации
        (на основе глобальных настроек).
        """
        data_dict = {
            "postgres_alchemy": postgres_alchemy.AuthDAL
        }
        return data_dict[self.db_name]()

    def choice_menu_obj(self) -> database.BaseMenu:
        """
        Метод выбирает объект для взаимодействия с данными меню
        (на основе глобальных настроек).
        """
        data_dict = {
            "postgres_alchemy": postgres_alchemy.MenuDAL
        }
        return data_dict[self.db_name]()

    def choice_changing_dish_obj(self) -> database.BaseChangingDish:
        """
        Метод выбирает объект для взаимодействия с данными по сомневающимся позициям
        (на основе глобальных настроек).
        """
        data_dict = {
            "postgres_alchemy": postgres_alchemy.ChangingDishDAL
        }
        return data_dict[self.db_name]()

    def choice_dish_obj(self) -> database.BaseDish:
        """
        Метод выбирает объект для взаимодействия с данными по блюдам
        (на основе глобальных настроек).
        """
        data_dict = {
            "postgres_alchemy": postgres_alchemy.DishDAL
        }
        return data_dict[self.db_name]()

    def choice_week_day_dish_obj(self) -> database.BaseWeekDayDish:
        """
        Метод выбирает объект для взаимодействия с данными по блюдам
        зависящих от дней недели
        (на основе глобальных настроек).
        """
        data_dict = {
            "postgres_alchemy": postgres_alchemy.WeekDayDishDAL
        }
        return data_dict[self.db_name]()

    def choice_r_keeper_credentials_obj(self) -> database.BaseRKeeperCredentials:
        """
        Метод выбирает объект для взаимодействия с авторизационными данными для доступа к r_keeper
        (на основе глобальных настроек).
        """
        data_dict = {
            "postgres_alchemy": postgres_alchemy.RKeeperCredentialsDAL
        }
        return data_dict[self.db_name]()

    def choice_r_keeper_dish_obj(self) -> database.BaseRKeeperDish:
        """
        Метод выбирает объект для взаимодействия с блюдами из r_keeper
        (на основе глобальных настроек).
        """
        data_dict = {
            "postgres_alchemy": postgres_alchemy.RKeeperDishDAL
        }
        return data_dict[self.db_name]()