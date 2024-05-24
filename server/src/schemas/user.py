from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.database.models import Role


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)


class UserResponse(BaseModel):
    id: int = 1
    username: str
    email: EmailStr
    avatar: str | None
    role: Role

    model_config = ConfigDict(from_attributes=True)  # noqa


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: Role
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    role: Role


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
