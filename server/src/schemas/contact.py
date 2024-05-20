from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class TagModel(BaseModel):
    name: str = Field(max_length=25)


class TagResponse(TagModel):
    id: int

    class Config:
        from_attributes = True


class NoteBase(BaseModel):
    title: str = Field(max_length=50)
    description: str = Field(max_length=150)


class NoteModel(NoteBase):
    tags: List[int]


class NoteUpdate(NoteModel):
    done: bool


class NoteStatusUpdate(BaseModel):
    done: bool


class NoteResponse(BaseModel):
    id: int
    created_at: datetime
    tags: List[TagResponse]

    class Config:
        from_attributes = True


class ContactBase(BaseModel):
    name: str = Field(min_length=3, max_length=25)
    lastname: str = Field(min_length=3, max_length=25)
    email: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    address: str = Field(max_length=100)
    birthday: Optional[date]


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int
    model_config = ConfigDict(from_attributes = True)  # noqa
