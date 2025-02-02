from typing import Union

from config import PAY_MANAGER

from .sber_pay.sber_pay_manager import SberPayManager
from .ingenico_pay.ingenico_pay_manager import IngenicoPay

def choice_pay_manager() -> SberPayManager:
    obj_dict = {
        "sberbank": SberPayManager,
        "ingenico": IngenicoPay
    }
    return obj_dict[PAY_MANAGER]()