from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ContactBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=20)
    subject: str = Field(min_length=2, max_length=200)
    message: str = Field(min_length=5)


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
