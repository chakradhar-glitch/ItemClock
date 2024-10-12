from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class ClockIn(BaseModel):
    email: EmailStr
    location: str
    insert_datetime: datetime = Field(default=datetime.utcnow())
