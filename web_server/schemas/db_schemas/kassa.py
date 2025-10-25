from typing import Optional

from pydantic import BaseModel


class KassaSchem(BaseModel):
    id: int
    name: str
    login: Optional[str]
    password: Optional[str]
    address: str
    food_point_id: int