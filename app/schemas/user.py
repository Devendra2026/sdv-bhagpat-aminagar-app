from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    role: str = Field(min_length=2, max_length=120)

class UserUpdate(UserBase):
    pass

class UserResponse(UserBase):
    id:int
    clerk_id:str
    created_at:datetime

    model_config = {"from_attributes": True}
