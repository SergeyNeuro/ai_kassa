from typing import Union

from config import PAY_MANAGER

from .sber_pay.sber_pay_manager import SberPayManager


def choice_pay_manager() -> SberPayManager:
    obj_dict = {
        "sberbank": SberPayManager
    }
    return obj_dict[PAY_MANAGER]()