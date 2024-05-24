from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime  # Import missing datetime

from src.schemas.tags import TagResponse

class PictureUpload(BaseModel):
    description: Optional[str] = None
    # tags: Optional[List[str]] = []

    class Config:
        orm_mode = True

class PictureUpdate(BaseModel):
    description: Optional[str] = None
    tags: Optional[List[str]] = []

    class Config:
        orm_mode = True

class PictureResponse(BaseModel):
    id: int
    image_url: str
    description: Optional[str]
    user_id: int
    # tags: List[TagResponse]  # Use TagResponse for consistency
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
