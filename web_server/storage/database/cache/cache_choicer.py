"""storage/database/cache/cache_choicer"""

# импортируем абстрактный интерфейс класс
from storage.base_interface.cache.cache_interface import BaseCache

# импортируем низкоуровневый объект для взаимодействия с КЭШем
from storage.database.cache.redis_cache import Redis


def get_cache_obj(key: str) -> BaseCache:
    """Данная функция возвращает объект для взаимодействия с КЭШем
    по ключу используя паттерн стратегия
    Args:
        key: ключ указывающий при помощи какого инструмента мы взаимодействуем с КЭШем
    """
    cache_obj_dict = {
        "redis": Redis
    }
    return cache_obj_dict[key]()
