from typing import Union

from config import CHECK_MANAGER

from .atol_pay.atol_pay import Atol


def choice_check_manager() -> Atol:
    obj_dict = {
        "atol": Atol
    }
    return obj_dict[CHECK_MANAGER]()