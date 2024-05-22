from pydantic import BaseModel, Field
from typing import List, Optional


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class PictureUpload(BaseModel):
    description: Optional[str] = None
    tags: Optional[List[str]] = []

    class Config:
        orm_mode = True


class PictureUpdate(BaseModel):
    description: Optional[str] = None
    tags: Optional[List[str]] = []


class PictureResponse(BaseModel):
    id: int
    image_url: str
    qr_code_url: Optional[str]
    description: Optional[str]
    tags: List[str]

    class Config:
        orm_mode = True
