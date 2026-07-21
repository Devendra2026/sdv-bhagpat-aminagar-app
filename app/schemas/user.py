from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    role: str = Field(min_length=2, max_length=120)

class UserResponse(UserUpdate):
    id:int
    clerk_id:str
    email: EmailStr
    created_at:datetime

    model_config = {"from_attributes": True}
