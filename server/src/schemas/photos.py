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
    qr_code_url: Optional[str]
    image_url: str
    description: Optional[str]
    tags: List[TagResponse]

    class Config:
        orm_mode = True
