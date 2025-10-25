from typing import Optional

from pydantic import BaseModel


class CustomersSchem(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    email: Optional[str]
    password: Optional[str]
    discount_type: Optional[int]