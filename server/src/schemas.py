from pydantic import BaseModel, field_validator, Field, EmailStr
from datetime import datetime
from typing import List, Optional


class PictureBase(BaseModel):
    description: str = None
    tags: str = None
    qr_code_url: str = None


class PictureUpload(BaseModel):
    id: int
    image_url: str
    qr_code_url: str
    description: str
    tags: List[str]

    class Config:
        orm_mode = True


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class PictureUpdate(BaseModel):
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class PictureResponse(BaseModel):
    id: int
    image_url: str
    description: Optional[str]
    tags: List[str]

    class Config:
        orm_mode = True
