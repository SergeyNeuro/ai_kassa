from typing import Optional

from pydantic import BaseModel


class DishSchem(BaseModel):
    id: int
    name: str
    menu_id: int
    code_name: str
    type: int
    count_type: int
    count: int
    price: int
    changing_dish_id: Optional[int] = None


class OperationSchem(BaseModel):
    success: bool
    info: str