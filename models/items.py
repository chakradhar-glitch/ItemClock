from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date


class Item(BaseModel):
    name: str
    email: EmailStr
    item_name: str
    quantity: int
    expiry_date: date
    insert_date: datetime = Field(default=datetime.utcnow())

class ItemUpdate(BaseModel):
    name: str
    email: EmailStr
    item_name: str
    quantity: int
    expiry_date: date
