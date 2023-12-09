from typing import Optional, Literal

from pydantic import BaseModel, constr, EmailStr, Field


class UserBase(BaseModel):
    first_name: str = Field(min_length=2, max_length=16)
    last_name: str = Field(min_length=3, max_length=20)
    email: EmailStr = Field(min_length=3)


class UserCreate(UserBase):
    # ДОБАВИТЬ РОЛИ ЕСЛИ НУЖНО
    role: Literal['user']
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr = Field(min_length=4)
    password: str = Field(min_length=6)


class UserInfo(UserBase):
    id: int = Field()
    role: str


class TokenData(BaseModel):
    id: int
    role: str