from pydantic import BaseModel
from typing import List, Optional


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
