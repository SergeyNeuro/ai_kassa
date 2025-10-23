from pydantic import BaseModel


class CreateIikoOrderSchem(BaseModel):
    item_id: str
    price: float
    amount: float