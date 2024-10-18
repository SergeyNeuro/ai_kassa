from typing import Optional
from pydantic import BaseModel

class DishSchem(BaseModel):
    name: Optional[str]
    menu_id: Optional[int]
    code_name: Optional[str]
    type: Optional[int]
    count_type: Optional[int]
    count: Optional[int]
    price: Optional[int]
    changing_dish_id: Optional[int]