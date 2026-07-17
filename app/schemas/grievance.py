from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class GrievanceBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    mobile_number: str = Field(min_length=7, max_length=20)
    email: EmailStr
    complaint_category: str = Field(min_length=2, max_length=120)
    municipal_ward: str = Field(min_length=2, max_length=60)
    incident_address: str = Field(min_length=5, max_length=255)
    description: str = Field(min_length=10)


class GrievanceCreate(GrievanceBase):
    pass


class GrievanceUpdate(GrievanceBase):
    status: str = Field(default="pending")


class GrievanceResponse(GrievanceBase):
    id: int
    status: str = Field(default="pending")
    created_at: datetime

    model_config = {"from_attributes": True}
