from pydantic import BaseModel
from datetime import datetime


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    pass


class CommentOut(CommentBase):
    id: int
    user_id: int
    picture_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
