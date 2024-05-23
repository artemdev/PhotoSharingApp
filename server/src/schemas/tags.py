from pydantic import BaseModel

class TagResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
